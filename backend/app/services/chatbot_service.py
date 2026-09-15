"""
AI Diagnostic Chatbot Service
================================
Provides conversational diagnostic assistance. Works fully offline
with a deterministic fallback using the project's own knowledge base.

Optional LLM integration via environment variables:
    LLM_PROVIDER=openai|anthropic|none
    LLM_API_KEY=...

The chatbot uses context from:
- Current sensor readings
- Recent diagnostics
- Device state
- Troubleshooting knowledge base
"""

import os
import re
from typing import Dict, List, Optional
from datetime import datetime

from backend.app.services.troubleshooting import TroubleshootingService


class ChatMessage:
    """A single chat message."""

    def __init__(self, role: str, content: str, metadata: dict = None):
        self.role = role  # "user" or "assistant"
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class ChatbotService:
    """
    AI-style diagnostic chatbot with deterministic fallback.

    The deterministic engine uses keyword extraction and the troubleshooting
    knowledge base to provide contextual responses. An external LLM can
    optionally enhance responses when API keys are configured.
    """

    def __init__(self):
        self.troubleshooting = TroubleshootingService()
        self.conversation_history: List[ChatMessage] = []
        self.llm_provider = os.getenv("LLM_PROVIDER", "none").lower()
        self.llm_api_key = os.getenv("LLM_API_KEY", "")
        self._llm_available = self.llm_provider != "none" and bool(self.llm_api_key)

        # Context storage
        self._current_device = None
        self._current_readings = None
        self._recent_diagnosis = None

    def set_context(self, device_id: str = None,
                    current_readings: dict = None,
                    recent_diagnosis: dict = None):
        """Update chatbot context with current system state."""
        if device_id:
            self._current_device = device_id
        if current_readings:
            self._current_readings = current_readings
        if recent_diagnosis:
            self._recent_diagnosis = recent_diagnosis

    def chat(self, user_message: str, context: dict = None) -> ChatMessage:
        """
        Process a user message and return a response.

        Args:
            user_message: The user's question or description.
            context: Optional additional context (device_id, readings, etc.)

        Returns:
            ChatMessage with the assistant's response.
        """
        # Store user message
        self.conversation_history.append(
            ChatMessage(role="user", content=user_message)
        )

        # Update context if provided
        if context:
            self.set_context(
                device_id=context.get("device_id"),
                current_readings=context.get("readings"),
                recent_diagnosis=context.get("diagnosis"),
            )

        # Try LLM first if available
        if self._llm_available:
            try:
                response = self._llm_response(user_message)
                if response:
                    msg = ChatMessage(
                        role="assistant", content=response,
                        metadata={"source": "llm", "provider": self.llm_provider}
                    )
                    self.conversation_history.append(msg)
                    return msg
            except Exception:
                pass  # Fall through to deterministic

        # Deterministic fallback
        response = self._deterministic_response(user_message)
        msg = ChatMessage(
            role="assistant", content=response,
            metadata={"source": "knowledge_base"}
        )
        self.conversation_history.append(msg)
        return msg

    def _deterministic_response(self, message: str) -> str:
        """
        Generate a response using keyword extraction and the knowledge base.
        """
        message_lower = message.lower().strip()

        # ── Greeting ──
        if any(g in message_lower for g in ["hello", "hi", "hey", "help", "start"]):
            return self._greeting_response()

        # ── Ask about specific fault ──
        fault_match = self._match_fault_type(message_lower)
        if fault_match:
            return self._fault_info_response(fault_match)

        # ── Symptom description ──
        symptom_results = self.troubleshooting.search_by_symptom(message)
        if symptom_results:
            return self._symptom_response(message, symptom_results)

        # ── Device/reading questions ──
        if any(w in message_lower for w in ["reading", "sensor", "status", "device", "panel", "motor"]):
            return self._device_context_response()

        # ── Safety questions ──
        if any(w in message_lower for w in ["safe", "danger", "risk", "hazard", "precaution"]):
            return self._safety_response()

        # ── What to check ──
        if any(w in message_lower for w in ["check", "inspect", "look for", "diagnose", "troubleshoot"]):
            return self._inspection_response()

        # ── Image-related ──
        if any(w in message_lower for w in ["image", "photo", "picture", "upload", "camera"]):
            return self._image_guidance_response()

        # ── Recent diagnosis ──
        if any(w in message_lower for w in ["result", "diagnosis", "report", "finding"]):
            return self._diagnosis_context_response()

        # ── Explanation questions ──
        if any(w in message_lower for w in ["what is", "what does", "explain", "why", "how does"]):
            return self._explanation_response(message_lower)

        # ── Default fallback ──
        return self._fallback_response()

    def _greeting_response(self) -> str:
        context_info = ""
        if self._current_device:
            context_info = f"\n\nI'm currently monitoring device **{self._current_device}**."
            if self._current_readings:
                r = self._current_readings
                context_info += (
                    f"\n- Temperature: {r.get('temperature', 'N/A')}°C"
                    f"\n- Current: {r.get('current', 'N/A')}A"
                    f"\n- Voltage: {r.get('voltage', 'N/A')}V"
                )

        return (
            "👋 Hello! I'm your **AI Electrical Diagnostic Assistant**.\n\n"
            "I can help you with:\n"
            "- 🔍 **Diagnosing electrical faults** — describe symptoms or upload images\n"
            "- 📊 **Interpreting sensor readings** — I'll analyze current, voltage, temperature, etc.\n"
            "- 🛠️ **Troubleshooting guidance** — step-by-step instructions for common faults\n"
            "- ⚡ **Understanding fault types** — ask about overheating, short circuits, etc.\n"
            "- 🔒 **Safety information** — proper procedures and precautions\n"
            f"{context_info}\n\n"
            "**How can I help you today?** Try describing what you're experiencing, "
            "like _\"My motor is getting unusually hot\"_ or _\"What should I check if the breaker keeps tripping?\"_\n\n"
            "_⚠ Note: I'm an AI diagnostic assistant, not a certified safety system. "
            "Always consult qualified personnel for electrical work._"
        )

    def _fault_info_response(self, fault_type: str) -> str:
        entry = self.troubleshooting.get_troubleshooting(fault_type)
        if not entry:
            return f"I don't have detailed information on '{fault_type}' faults."

        causes_text = "\n".join(f"  • {c}" for c in entry.possible_causes[:5])
        actions_text = "\n".join(f"  • {a}" for a in entry.recommended_actions[:4])
        safety_text = "\n".join(f"  {w}" for w in entry.safety_warnings[:3])

        return (
            f"## ⚡ {fault_type}\n\n"
            f"{entry.description}\n\n"
            f"### Possible Causes:\n{causes_text}\n\n"
            f"### Recommended Actions:\n{actions_text}\n\n"
            f"### Safety Warnings:\n{safety_text}\n\n"
            f"Would you like me to go into more detail on any of these points, "
            f"or help you with specific troubleshooting steps?"
        )

    def _symptom_response(self, symptom: str, results: list) -> str:
        if not results:
            return self._fallback_response()

        top = results[0]
        response = (
            f"Based on your description: _\"{symptom}\"_\n\n"
            f"This could indicate **{top['fault_type']}**.\n\n"
            f"📋 **{top['description']}**\n\n"
        )

        if top.get("possible_causes"):
            causes = "\n".join(f"  • {c}" for c in top["possible_causes"][:4])
            response += f"### Possible Causes:\n{causes}\n\n"

        if top.get("recommended_actions"):
            actions = "\n".join(f"  • {a}" for a in top["recommended_actions"][:3])
            response += f"### What To Do:\n{actions}\n\n"

        if len(results) > 1:
            others = ", ".join(r["fault_type"] for r in results[1:3])
            response += f"_Other possibilities: {others}_\n\n"

        if top.get("safety_warnings"):
            response += f"### ⚠ Safety:\n  {top['safety_warnings'][0]}\n\n"

        return response

    def _device_context_response(self) -> str:
        if self._current_readings:
            r = self._current_readings
            status_items = []
            for key, value in r.items():
                if isinstance(value, (int, float)):
                    status_items.append(f"  - **{key}**: {value}")
            readings_text = "\n".join(status_items)

            response = f"### 📊 Current Readings"
            if self._current_device:
                response += f" — {self._current_device}"
            response += f"\n\n{readings_text}\n\n"

            # Quick analysis
            if r.get("temperature", 0) > 60:
                response += "⚠ Temperature is above normal. Monitor for overheating.\n"
            if r.get("current", 0) > 18:
                response += "⚠ Current draw is elevated. Check for overload.\n"
            if r.get("voltage", 230) < 210 or r.get("voltage", 230) > 250:
                response += "⚠ Voltage is outside normal range.\n"

            return response + "\nWould you like a full diagnostic analysis?"
        else:
            return (
                "I don't have current sensor readings in context.\n\n"
                "You can:\n"
                "- Navigate to the **Dashboard** to see real-time readings\n"
                "- Use the **Diagnostics** page to submit sensor values for analysis\n"
                "- Ask me about a specific fault type or symptom"
            )

    def _safety_response(self) -> str:
        return (
            "## 🔒 Electrical Safety Guidelines\n\n"
            "### General Safety Rules:\n"
            "  1. **Never work on energized equipment** without proper authorization and PPE.\n"
            "  2. **Isolate power** before performing any inspection or repair.\n"
            "  3. **Verify isolation** using a tested voltage detector.\n"
            "  4. **Use appropriate PPE** — insulated gloves, safety glasses, arc-rated clothing.\n"
            "  5. **Follow lockout/tagout** procedures.\n"
            "  6. **Have a qualified partner** present for any electrical work.\n\n"
            "### If You Suspect a Fault:\n"
            "  • Do not touch the equipment if you smell burning or see smoke.\n"
            "  • Evacuate the area if there is a fire risk.\n"
            "  • Report the issue to qualified maintenance personnel.\n"
            "  • Do not attempt repairs beyond your qualification level.\n\n"
            "### Emergency:\n"
            "  🚨 In case of electrical fire, use a **Class C fire extinguisher**.\n"
            "  🚨 In case of electrical shock, **do NOT touch the person** — isolate power first.\n\n"
            "_This system is a diagnostic aid. All repairs should be performed by "
            "qualified, authorized personnel following applicable safety standards._"
        )

    def _inspection_response(self) -> str:
        context = ""
        if self._recent_diagnosis:
            fault = self._recent_diagnosis.get("fault_type", "Unknown")
            context = f"\nBased on the recent diagnosis of **{fault}**, "
            entry = self.troubleshooting.get_troubleshooting(fault)
            if entry:
                steps = "\n".join(f"  {s}" for s in entry.diagnostic_steps[:6])
                return (
                    f"### 🔍 Inspection Checklist for {fault}\n\n"
                    f"{steps}\n\n"
                    f"⚠ Always isolate power before physical inspection.\n\n"
                    f"Would you like safety warnings or more detailed guidance?"
                )

        return (
            "### 🔍 General Electrical Inspection Checklist\n\n"
            "  1. **Visual inspection** — Look for burn marks, discoloration, corrosion, damaged insulation.\n"
            "  2. **Temperature check** — Use non-contact IR thermometer for hot spots.\n"
            "  3. **Connection tightness** — Check terminal connections (with power OFF).\n"
            "  4. **Insulation test** — Megger test for insulation resistance.\n"
            "  5. **Load verification** — Compare current draw against rated capacity.\n"
            "  6. **Environmental check** — Ventilation, moisture, contamination.\n\n"
            "⚠ **Always isolate power before physical inspection.**\n\n"
            "Can you describe what specific issue you're investigating?"
        )

    def _image_guidance_response(self) -> str:
        return (
            "### 📷 Image Analysis Guide\n\n"
            "You can upload an image of your electrical component or panel for AI analysis.\n\n"
            "**For best results:**\n"
            "  • Take a clear, well-lit photo of the component\n"
            "  • Capture any visible damage, discoloration, or burn marks\n"
            "  • Include the full component in the frame\n"
            "  • Thermal/infrared images are also supported\n\n"
            "**The AI can detect:**\n"
            "  • Burn marks and heat damage\n"
            "  • Corrosion and oxidation\n"
            "  • Discoloration\n"
            "  • Surface cracking\n"
            "  • Thermal hotspots (in IR images)\n\n"
            "Navigate to the **Diagnostics** page to upload an image, "
            "or use the **AR Guidance** page for camera-based analysis.\n\n"
            "_Note: Image analysis is an assistive tool and cannot replace professional inspection._"
        )

    def _diagnosis_context_response(self) -> str:
        if self._recent_diagnosis:
            d = self._recent_diagnosis
            return (
                f"### 📋 Recent Diagnostic Result\n\n"
                f"  **Fault Detected:** {d.get('fault_type', 'Unknown')}\n"
                f"  **Confidence:** {d.get('confidence', 0):.1%}\n"
                f"  **Severity:** {d.get('severity', 'N/A')}\n"
                f"  **Risk Score:** {d.get('risk_score', 0)}/100\n\n"
                f"Would you like me to explain the diagnosis, provide troubleshooting "
                f"steps, or discuss the recommended actions?"
            )
        return (
            "No recent diagnostic results are available.\n\n"
            "You can run a diagnosis by:\n"
            "- Submitting sensor readings on the **Diagnostics** page\n"
            "- Uploading an image for visual analysis\n"
            "- Describing symptoms here and I'll provide guidance"
        )

    def _explanation_response(self, message: str) -> str:
        explanations = {
            "power factor": (
                "**Power Factor** is the ratio of real power (W) to apparent power (VA). "
                "A power factor of 1.0 means all power is being used effectively. "
                "Low power factor (< 0.85) indicates wasted energy and can cause overheating, "
                "increased current draw, and voltage drops."
            ),
            "overcurrent": (
                "**Overcurrent** occurs when the current flowing through a circuit exceeds its rated capacity. "
                "This can be caused by overloading, short circuits, or motor faults. "
                "Protective devices like circuit breakers and fuses are designed to interrupt overcurrent."
            ),
            "overvoltage": (
                "**Overvoltage** is when supply voltage exceeds the normal range (typically >250V for 230V systems). "
                "It can damage sensitive equipment, reduce insulation life, and cause component failure."
            ),
            "insulation resistance": (
                "**Insulation Resistance** measures how well the insulation around conductors prevents current leakage. "
                "Low insulation resistance indicates degraded insulation, which can lead to "
                "shock hazard, short circuits, or ground faults."
            ),
            "arc flash": (
                "**Arc Flash** is an explosive release of energy caused by an electrical arc. "
                "It can produce temperatures over 35,000°F, intense light, pressure waves, and shrapnel. "
                "Arc flash is a potentially fatal hazard."
            ),
            "frequency": (
                "**Frequency** in AC power systems (typically 50Hz or 60Hz) indicates the rate of "
                "alternation. Deviations from normal frequency can indicate generator or grid instability "
                "and can affect motor speed and equipment operation."
            ),
        }

        for keyword, explanation in explanations.items():
            if keyword in message:
                return explanation

        return (
            "I can explain many electrical concepts. Try asking about:\n"
            "  • Power factor\n"
            "  • Overcurrent\n"
            "  • Overvoltage\n"
            "  • Insulation resistance\n"
            "  • Arc flash\n"
            "  • Specific fault types (overheating, short circuit, etc.)\n\n"
            "Or describe what you'd like to understand better."
        )

    def _fallback_response(self) -> str:
        return (
            "I'm not sure I fully understand your question. Here's how I can help:\n\n"
            "  💡 **Describe a symptom** — _\"My motor is getting hot\"_\n"
            "  💡 **Ask about a fault** — _\"What causes a short circuit?\"_\n"
            "  💡 **Request inspection steps** — _\"What should I check first?\"_\n"
            "  💡 **Safety info** — _\"What safety precautions should I take?\"_\n"
            "  💡 **Get sensor analysis** — _\"What do my current readings mean?\"_\n\n"
            "You can also use the **Diagnostics** page for sensor-based or image-based analysis."
        )

    def _match_fault_type(self, message: str) -> Optional[str]:
        """Try to match message to a specific fault type."""
        fault_keywords = {
            "overheating": "Overheating",
            "overheat": "Overheating",
            "short circuit": "Short Circuit",
            "overvoltage": "Overvoltage",
            "over voltage": "Overvoltage",
            "undervoltage": "Undervoltage",
            "under voltage": "Undervoltage",
            "overcurrent": "Overcurrent",
            "over current": "Overcurrent",
            "loose connection": "Loose Connection",
            "burnt": "Burnt Component",
            "burned": "Burnt Component",
            "insulation": "Insulation Damage",
            "corrosion": "Corrosion",
        }

        for keyword, fault_type in fault_keywords.items():
            # Match "what is X" or "tell me about X" patterns
            if keyword in message and any(q in message for q in
                    ["what", "tell", "explain", "about", "cause", "how"]):
                return fault_type

        return None

    def _llm_response(self, message: str) -> Optional[str]:
        """
        Attempt to get an LLM response (placeholder for real integration).

        To integrate a real LLM:
        1. Set LLM_PROVIDER and LLM_API_KEY environment variables
        2. Implement the API call for your chosen provider
        3. Include system prompt with safety guidelines
        """
        # This is where you would integrate an actual LLM API
        # For now, return None to use deterministic fallback
        return None

    def get_history(self, limit: int = 20) -> List[dict]:
        """Get conversation history."""
        return [msg.to_dict() for msg in self.conversation_history[-limit:]]

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
