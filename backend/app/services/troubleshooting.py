"""
Troubleshooting Knowledge Base
================================
Comprehensive knowledge base for all 10 fault categories.
Each entry includes causes, diagnostic steps, recommended actions,
safety warnings, and escalation conditions.

SAFETY NOTE: This application is a diagnostic AID, not a certified
electrical safety system. Always follow proper safety procedures.
Power should be isolated and qualified personnel should handle
hazardous electrical work.
"""

from typing import Dict, List, Optional


class TroubleshootingEntry:
    """A single troubleshooting knowledge base entry."""

    def __init__(
        self,
        fault_type: str,
        description: str,
        possible_causes: List[str],
        diagnostic_steps: List[str],
        recommended_actions: List[str],
        safety_warnings: List[str],
        escalation_conditions: List[str],
        preventive_measures: List[str],
    ):
        self.fault_type = fault_type
        self.description = description
        self.possible_causes = possible_causes
        self.diagnostic_steps = diagnostic_steps
        self.recommended_actions = recommended_actions
        self.safety_warnings = safety_warnings
        self.escalation_conditions = escalation_conditions
        self.preventive_measures = preventive_measures

    def to_dict(self) -> dict:
        return {
            "fault_type": self.fault_type,
            "description": self.description,
            "possible_causes": self.possible_causes,
            "diagnostic_steps": self.diagnostic_steps,
            "recommended_actions": self.recommended_actions,
            "safety_warnings": self.safety_warnings,
            "escalation_conditions": self.escalation_conditions,
            "preventive_measures": self.preventive_measures,
        }


# ═══════════════════════════════════════════════════════════════
#  COMPLETE TROUBLESHOOTING KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════

KNOWLEDGE_BASE: Dict[str, TroubleshootingEntry] = {

    "Normal": TroubleshootingEntry(
        fault_type="Normal",
        description="All sensor readings are within normal operating parameters. No fault detected.",
        possible_causes=[],
        diagnostic_steps=[
            "Continue routine monitoring.",
            "Verify that all sensor readings remain stable.",
            "Review historical data for any developing trends.",
        ],
        recommended_actions=[
            "No immediate action required.",
            "Maintain regular inspection schedule.",
            "Ensure environmental conditions remain stable.",
        ],
        safety_warnings=[
            "Always follow standard electrical safety procedures during routine inspections.",
        ],
        escalation_conditions=[
            "Any sudden change in readings from normal baseline.",
            "Unusual sounds, smells, or visual indicators despite normal readings.",
        ],
        preventive_measures=[
            "Regular scheduled maintenance.",
            "Periodic thermal imaging surveys.",
            "Calibration of monitoring sensors.",
        ],
    ),

    "Overheating": TroubleshootingEntry(
        fault_type="Overheating",
        description="Temperature is significantly above normal operating range. This can lead to insulation failure, component damage, or fire hazard if not addressed.",
        possible_causes=[
            "Electrical overload — drawing more current than rated capacity.",
            "Loose or corroded connection causing resistive heating.",
            "Poor ventilation or blocked cooling pathways.",
            "Component degradation or aging.",
            "Ambient temperature exceeding design specifications.",
            "Harmonic distortion causing additional heating.",
            "Insufficient conductor sizing for the load.",
        ],
        diagnostic_steps=[
            "1. Disconnect power if safe to do so and the situation appears dangerous.",
            "2. Use a non-contact infrared thermometer to confirm temperature readings.",
            "3. Inspect the affected component and surrounding area for visible heat damage.",
            "4. Check current draw against rated capacity.",
            "5. Inspect all terminal connections for tightness and discoloration.",
            "6. Verify ventilation and cooling systems are operational.",
            "7. Review load history to identify overload patterns.",
            "8. Check for signs of insulation deterioration.",
        ],
        recommended_actions=[
            "Reduce load on the affected circuit if possible.",
            "Inspect and tighten all connections in the affected area.",
            "Improve ventilation or cooling around the equipment.",
            "Schedule professional inspection before returning to full operation.",
            "Replace degraded components as identified.",
        ],
        safety_warnings=[
            "🚨 Do NOT touch exposed conductors or overheated surfaces.",
            "🚨 Do NOT perform live electrical work. Isolate power first.",
            "🚨 If there is any sign of fire or smoke, evacuate and call emergency services.",
            "Use appropriate PPE including insulated gloves and eye protection.",
            "Ensure a fire extinguisher rated for electrical fires (Class C) is accessible.",
        ],
        escalation_conditions=[
            "Temperature exceeds 100°C and continues rising.",
            "Visible smoke, melting, or discoloration.",
            "Burning smell from electrical equipment.",
            "Circuit breaker fails to trip despite overload.",
            "Multiple components showing elevated temperatures simultaneously.",
        ],
        preventive_measures=[
            "Regular thermal imaging inspections.",
            "Torque verification of all connections.",
            "Load monitoring to prevent overload conditions.",
            "Adequate ventilation design and maintenance.",
            "Use of thermal protection devices.",
        ],
    ),

    "Short Circuit": TroubleshootingEntry(
        fault_type="Short Circuit",
        description="An unintended low-resistance path is allowing excessive current flow. This is a potentially dangerous condition that can cause equipment damage, arc flash, or fire.",
        possible_causes=[
            "Damaged wire insulation allowing conductor contact.",
            "Moisture ingress causing conductive paths.",
            "Foreign object creating an unintended bridge between conductors.",
            "Component failure creating an internal short.",
            "Mechanical damage to wiring or equipment.",
            "Rodent damage to cable insulation.",
            "Manufacturing defect in equipment.",
        ],
        diagnostic_steps=[
            "1. IMMEDIATELY isolate power to the affected circuit.",
            "2. Do NOT attempt to reset breakers until the cause is identified.",
            "3. Inspect wiring for visible damage, burn marks, or melted insulation.",
            "4. Use an insulation resistance tester (megger) to test conductor insulation.",
            "5. Systematically disconnect loads to isolate the fault location.",
            "6. Inspect junction boxes and connection points.",
            "7. Check for moisture intrusion or contamination.",
            "8. Verify protective devices operated correctly.",
        ],
        recommended_actions=[
            "Keep power isolated until the fault is located and repaired.",
            "Replace damaged wiring or components.",
            "Verify protective devices (fuses, breakers) are correctly rated.",
            "Engage a qualified electrician for repair.",
            "Test the circuit before restoring power.",
        ],
        safety_warnings=[
            "🚨 SHORT CIRCUITS CAN CAUSE ARC FLASH — a life-threatening hazard.",
            "🚨 NEVER attempt to reset a breaker without identifying the fault cause.",
            "🚨 Do NOT handle damaged wiring without isolating power first.",
            "🚨 If arc damage is visible, assume the area is unsafe until inspected.",
            "Keep personnel away from the affected area.",
            "Use appropriate arc-rated PPE if live diagnostics are required.",
        ],
        escalation_conditions=[
            "Arc flash damage observed.",
            "Multiple protective devices have tripped.",
            "Smoke or fire present.",
            "Fault cannot be located.",
            "Structural damage to electrical enclosure.",
        ],
        preventive_measures=[
            "Regular insulation resistance testing.",
            "Cable management to prevent mechanical damage.",
            "Environmental protection (moisture, dust, rodents).",
            "Arc fault circuit interrupter (AFCI) installation where applicable.",
            "Regular visual inspection of wiring and connections.",
        ],
    ),

    "Overvoltage": TroubleshootingEntry(
        fault_type="Overvoltage",
        description="Supply voltage is significantly above the normal operating range. Sustained overvoltage can damage sensitive equipment and reduce component lifespan.",
        possible_causes=[
            "Utility supply voltage fluctuation.",
            "Transformer tap setting incorrect.",
            "Load shedding causing voltage rise on lightly loaded circuits.",
            "Generator voltage regulator malfunction.",
            "Lightning-induced transient overvoltage.",
            "Switching surges in the power system.",
            "Faulty voltage regulator.",
        ],
        diagnostic_steps=[
            "1. Measure voltage at the point of supply and at the affected equipment.",
            "2. Check if overvoltage affects the entire facility or specific circuits.",
            "3. Review voltage history/trending data.",
            "4. Inspect transformer tap settings if accessible.",
            "5. Check for recent load changes in the facility.",
            "6. Verify voltage regulator operation if installed.",
            "7. Contact the utility provider if supply voltage is out of specification.",
        ],
        recommended_actions=[
            "Disconnect sensitive equipment until voltage is stabilized.",
            "Install or verify surge protection devices.",
            "Adjust transformer taps if applicable.",
            "Contact utility provider to report sustained overvoltage.",
            "Consider installing automatic voltage regulators.",
        ],
        safety_warnings=[
            "⚠ Overvoltage can cause insulation breakdown and equipment failure.",
            "⚠ Do not operate sensitive electronic equipment during overvoltage events.",
            "⚠ If equipment is sparking or smoking due to overvoltage, isolate power immediately.",
        ],
        escalation_conditions=[
            "Voltage exceeds 110% of nominal and is sustained.",
            "Equipment damage has already occurred.",
            "Overvoltage is recurring frequently.",
            "Surge protection devices have operated (need replacement).",
        ],
        preventive_measures=[
            "Install surge protection devices (SPDs) at service entrance.",
            "Voltage monitoring and alarming.",
            "Automatic voltage regulators for sensitive equipment.",
            "Regular utility coordination for voltage quality.",
        ],
    ),

    "Undervoltage": TroubleshootingEntry(
        fault_type="Undervoltage",
        description="Supply voltage is significantly below the expected range. Undervoltage can cause motors to draw excessive current, leading to overheating and premature failure.",
        possible_causes=[
            "Utility supply voltage sag.",
            "Overloaded circuit or distribution transformer.",
            "Long cable runs with excessive voltage drop.",
            "Poor connections causing voltage drop.",
            "Large motor starting on the same circuit.",
            "Undersized conductors for the load.",
            "Transformer tap setting incorrect.",
        ],
        diagnostic_steps=[
            "1. Measure voltage at the service entrance and at the affected equipment.",
            "2. Calculate voltage drop across the circuit.",
            "3. Check for overloaded circuits or transformers.",
            "4. Inspect connections for looseness or corrosion.",
            "5. Review if undervoltage coincides with specific load events.",
            "6. Verify conductor sizing against load requirements.",
            "7. Check transformer loading and tap positions.",
        ],
        recommended_actions=[
            "Identify and correct the source of voltage drop.",
            "Tighten and clean all connections.",
            "Redistribute loads to balance circuits.",
            "Upgrade conductor sizes if voltage drop is excessive.",
            "Install undervoltage protection relays for critical equipment.",
        ],
        safety_warnings=[
            "⚠ Motors running under undervoltage draw excessive current — monitor for overheating.",
            "⚠ Do not continue operating equipment significantly below rated voltage.",
        ],
        escalation_conditions=[
            "Voltage below 90% of nominal sustained.",
            "Motors overheating due to undervoltage.",
            "Equipment malfunction or shutdown.",
            "Undervoltage affecting critical systems.",
        ],
        preventive_measures=[
            "Voltage monitoring at critical points.",
            "Proper conductor sizing during installation.",
            "Regular connection maintenance.",
            "Load management to prevent circuit overloading.",
        ],
    ),

    "Overcurrent": TroubleshootingEntry(
        fault_type="Overcurrent",
        description="Current draw is significantly above the normal rated capacity. Sustained overcurrent causes heating and can lead to insulation damage, equipment failure, or fire.",
        possible_causes=[
            "Electrical overload — too many loads on the circuit.",
            "Motor mechanical binding or bearing failure.",
            "Partial short circuit (developing fault).",
            "Undersized protective devices.",
            "Phase loss in three-phase systems.",
            "Blocked ventilation causing motor to work harder.",
            "Process or load change requiring more power.",
        ],
        diagnostic_steps=[
            "1. Measure current draw on the affected circuit.",
            "2. Compare measured current against rated capacity.",
            "3. Identify all loads on the circuit.",
            "4. Check if overcurrent is continuous or intermittent.",
            "5. Inspect motors for mechanical issues.",
            "6. Verify protective device ratings.",
            "7. Check for phase imbalance in three-phase systems.",
        ],
        recommended_actions=[
            "Reduce load on the affected circuit.",
            "Disconnect non-essential loads.",
            "Inspect equipment for mechanical issues.",
            "Verify and upgrade protective devices if undersized.",
            "Schedule professional evaluation of the electrical system.",
        ],
        safety_warnings=[
            "🚨 Sustained overcurrent is a fire hazard.",
            "🚨 If protective devices are not tripping, there is a coordination problem — escalate immediately.",
            "⚠ Do not bypass or upsize fuses/breakers without an engineering evaluation.",
        ],
        escalation_conditions=[
            "Current exceeds 150% of rated capacity.",
            "Protective devices failing to trip.",
            "Visible heat damage.",
            "Repeated breaker trips.",
        ],
        preventive_measures=[
            "Current monitoring and trending.",
            "Regular motor maintenance.",
            "Proper circuit sizing and protection coordination.",
            "Load management programs.",
        ],
    ),

    "Loose Connection": TroubleshootingEntry(
        fault_type="Loose Connection",
        description="Electrical connections are not properly secured, causing intermittent contact, resistive heating, and voltage fluctuations. This is one of the most common causes of electrical fires.",
        possible_causes=[
            "Thermal cycling loosening terminal connections.",
            "Vibration loosening connections over time.",
            "Improper initial installation or torquing.",
            "Corrosion at connection points.",
            "Wrong connector type for the application.",
            "Aluminum conductor connections without anti-oxidant compound.",
        ],
        diagnostic_steps=[
            "1. Use thermal imaging to identify hot connections (if power is on and safe).",
            "2. Isolate power before physical inspection.",
            "3. Check all terminal connections for tightness.",
            "4. Look for discoloration, melting, or oxidation at connections.",
            "5. Measure resistance across suspected connections.",
            "6. Check for voltage fluctuations indicating intermittent contact.",
            "7. Inspect both line and load side connections.",
        ],
        recommended_actions=[
            "Isolate power and re-torque all connections to manufacturer specifications.",
            "Clean corroded connections and apply appropriate compound.",
            "Replace damaged connectors, lugs, or terminals.",
            "Use calibrated torque tools for all reconnections.",
            "Schedule follow-up thermal imaging to confirm repair.",
        ],
        safety_warnings=[
            "🚨 Loose connections are a leading cause of electrical fires.",
            "🚨 Always isolate power before tightening connections.",
            "⚠ Overheated connections may have weakened conductors — inspect carefully.",
        ],
        escalation_conditions=[
            "Visible arcing or spark damage at connections.",
            "Melted insulation around connection points.",
            "Connections that loosen repeatedly after tightening.",
            "Multiple loose connections found in the same panel.",
        ],
        preventive_measures=[
            "Regular thermal imaging inspections.",
            "Torque verification programs.",
            "Anti-oxidant compound on aluminum connections.",
            "Vibration dampening for connections subject to mechanical vibration.",
        ],
    ),

    "Burnt Component": TroubleshootingEntry(
        fault_type="Burnt Component",
        description="A component has sustained thermal damage. This typically indicates a sustained fault condition, component failure, or design/installation deficiency.",
        possible_causes=[
            "Sustained overload beyond component rating.",
            "Short circuit through or near the component.",
            "Loose connection causing localized heating.",
            "Component quality or manufacturing defect.",
            "End of component service life.",
            "Environmental factors (moisture, contamination).",
            "Inadequate component rating for the application.",
        ],
        diagnostic_steps=[
            "1. Isolate power to the affected equipment.",
            "2. Identify the burnt component and its function in the circuit.",
            "3. Determine the likely cause of the burn (overload, short, connection).",
            "4. Inspect adjacent components for collateral damage.",
            "5. Test insulation resistance of nearby wiring.",
            "6. Review maintenance and operational history.",
            "7. Check if the component was correctly rated for the application.",
        ],
        recommended_actions=[
            "Do NOT re-energize without replacing the damaged component.",
            "Replace the component with one of correct rating.",
            "Address the root cause (overload, connection issue, etc.).",
            "Inspect and clean the surrounding area.",
            "Test the circuit before restoring power.",
            "Engage a qualified electrician for evaluation and repair.",
        ],
        safety_warnings=[
            "🚨 Burnt components may have compromised insulation — risk of shock.",
            "🚨 Do NOT re-energize until a qualified person has inspected and repaired.",
            "🚨 Check for structural damage to enclosures that may have been weakened.",
            "⚠ Burnt component fumes may be toxic — ensure adequate ventilation.",
        ],
        escalation_conditions=[
            "Multiple components damaged.",
            "Enclosure or structural damage.",
            "Root cause unclear.",
            "Recurring component failures in the same location.",
        ],
        preventive_measures=[
            "Proper component sizing and rating.",
            "Regular thermal monitoring.",
            "Protective device coordination studies.",
            "Component quality verification.",
        ],
    ),

    "Insulation Damage": TroubleshootingEntry(
        fault_type="Insulation Damage",
        description="Electrical insulation has degraded, creating a risk of leakage current, short circuit, or electrical shock. Insulation failure is progressive and worsens over time.",
        possible_causes=[
            "Thermal aging from prolonged overheating.",
            "Mechanical damage from abrasion, crushing, or bending.",
            "Moisture ingress degrading insulation properties.",
            "Chemical exposure or contamination.",
            "UV radiation exposure (outdoor installations).",
            "Rodent or pest damage.",
            "Voltage stress beyond insulation rating.",
            "Normal aging at end of insulation service life.",
        ],
        diagnostic_steps=[
            "1. Perform insulation resistance testing (megger test).",
            "2. Compare results against minimum acceptable values.",
            "3. Visually inspect accessible wiring for cracking, discoloration, or damage.",
            "4. Check for moisture or contamination in the area.",
            "5. Review the age and service conditions of the insulation.",
            "6. Measure leakage current if possible.",
            "7. Check ground fault protection operation.",
        ],
        recommended_actions=[
            "Replace wiring or components with compromised insulation.",
            "Address environmental factors (moisture, heat, chemicals).",
            "Install ground fault protection if not present.",
            "Schedule re-testing to monitor insulation condition.",
            "Engage a qualified electrician for repair.",
        ],
        safety_warnings=[
            "🚨 Damaged insulation creates a SHOCK HAZARD.",
            "🚨 Do not touch potentially damaged wiring without proper isolation.",
            "⚠ Insulation failure can cause arcing leading to fire.",
            "⚠ Ground fault protection may be the only defense — ensure it is functional.",
        ],
        escalation_conditions=[
            "Insulation resistance below minimum acceptable values.",
            "Active leakage current detected.",
            "Ground fault protection devices tripping.",
            "Visible arcing or tracking marks on insulation.",
        ],
        preventive_measures=[
            "Scheduled insulation resistance testing program.",
            "Environmental protection (sealing, ventilation).",
            "Proper cable routing to prevent mechanical damage.",
            "Ground fault protection on all circuits.",
        ],
    ),

    "Corrosion": TroubleshootingEntry(
        fault_type="Corrosion",
        description="Corrosion of electrical connections, contacts, or components. Corrosion increases resistance, generates heat, and can cause intermittent or permanent failure.",
        possible_causes=[
            "Moisture exposure in humid environments.",
            "Galvanic corrosion from dissimilar metal contacts.",
            "Chemical contamination (salt, acids, industrial chemicals).",
            "Outdoor exposure without adequate weatherproofing.",
            "Condensation within enclosures.",
            "Age-related oxidation of copper or aluminum conductors.",
        ],
        diagnostic_steps=[
            "1. Visually inspect connections for green (copper), white (aluminum), or red (iron) oxidation.",
            "2. Measure resistance across suspected corroded connections.",
            "3. Use thermal imaging to find hot spots caused by corroded connections.",
            "4. Check enclosure sealing and weatherproofing.",
            "5. Assess the environment for corrosive agents.",
            "6. Inspect fastener and hardware condition.",
        ],
        recommended_actions=[
            "Clean corroded connections using appropriate methods and compounds.",
            "Apply anti-corrosion coating or compound to cleaned connections.",
            "Replace severely corroded components.",
            "Improve environmental protection (sealing, ventilation, dehumidification).",
            "Use corrosion-resistant materials in harsh environments.",
        ],
        safety_warnings=[
            "⚠ Corroded connections can fail unpredictably.",
            "⚠ Always isolate power before cleaning or replacing connections.",
            "⚠ Use appropriate cleaning agents — some are flammable or conductive.",
        ],
        escalation_conditions=[
            "Severe corrosion causing structural weakness of components.",
            "Corroded connections causing equipment malfunction.",
            "Widespread corrosion indicating environmental control failure.",
            "Corrosion on critical safety equipment.",
        ],
        preventive_measures=[
            "Environmental monitoring (humidity, temperature).",
            "Use of anti-corrosion compounds on connections.",
            "Proper enclosure ratings for the environment (NEMA/IP).",
            "Regular visual inspection and maintenance.",
            "Use of corrosion-resistant materials and coatings.",
        ],
    ),
}


class TroubleshootingService:
    """Service for retrieving troubleshooting guidance."""

    def get_troubleshooting(self, fault_type: str) -> Optional[TroubleshootingEntry]:
        """Get troubleshooting entry for a fault type."""
        return KNOWLEDGE_BASE.get(fault_type)

    def get_all_fault_types(self) -> List[str]:
        """Get all supported fault types."""
        return list(KNOWLEDGE_BASE.keys())

    def get_all_entries(self) -> Dict[str, dict]:
        """Get all troubleshooting entries as dicts."""
        return {k: v.to_dict() for k, v in KNOWLEDGE_BASE.items()}

    def get_causes_for_fault(self, fault_type: str) -> List[str]:
        """Get possible causes for a fault type."""
        entry = KNOWLEDGE_BASE.get(fault_type)
        return entry.possible_causes if entry else []

    def get_actions_for_fault(self, fault_type: str) -> List[str]:
        """Get recommended actions for a fault type."""
        entry = KNOWLEDGE_BASE.get(fault_type)
        return entry.recommended_actions if entry else []

    def get_safety_warnings_for_fault(self, fault_type: str) -> List[str]:
        """Get safety warnings for a fault type."""
        entry = KNOWLEDGE_BASE.get(fault_type)
        return entry.safety_warnings if entry else [
            "⚠ Follow standard electrical safety procedures.",
            "🚨 Never work on energized electrical equipment without proper authorization and PPE.",
        ]

    def search_by_symptom(self, symptom: str) -> List[dict]:
        """
        Search the knowledge base by symptom description.
        Returns matching fault entries ranked by relevance.
        """
        symptom_lower = symptom.lower()
        results = []

        # Keyword mappings
        symptom_keywords = {
            "hot": ["Overheating", "Overcurrent", "Loose Connection", "Burnt Component"],
            "heat": ["Overheating", "Overcurrent", "Loose Connection", "Burnt Component"],
            "warm": ["Overheating", "Loose Connection"],
            "spark": ["Short Circuit", "Loose Connection"],
            "arc": ["Short Circuit", "Loose Connection", "Insulation Damage"],
            "trip": ["Overcurrent", "Short Circuit", "Overheating"],
            "breaker": ["Overcurrent", "Short Circuit"],
            "flicker": ["Loose Connection", "Undervoltage"],
            "fluctuat": ["Loose Connection", "Undervoltage", "Overvoltage"],
            "smoke": ["Overheating", "Short Circuit", "Burnt Component"],
            "burn": ["Burnt Component", "Overheating", "Short Circuit"],
            "smell": ["Overheating", "Burnt Component", "Insulation Damage"],
            "noise": ["Loose Connection", "Overcurrent", "Overheating"],
            "vibrat": ["Loose Connection", "Overheating"],
            "corrosi": ["Corrosion"],
            "rust": ["Corrosion"],
            "green": ["Corrosion"],
            "shock": ["Insulation Damage"],
            "tingle": ["Insulation Damage"],
            "leak": ["Insulation Damage"],
            "crack": ["Insulation Damage"],
            "dim": ["Undervoltage"],
            "low voltage": ["Undervoltage"],
            "high voltage": ["Overvoltage"],
            "surge": ["Overvoltage"],
            "motor": ["Overheating", "Overcurrent"],
            "transformer": ["Overheating", "Overcurrent", "Insulation Damage"],
        }

        matched_faults = set()
        for keyword, faults in symptom_keywords.items():
            if keyword in symptom_lower:
                matched_faults.update(faults)

        for fault_type in matched_faults:
            entry = KNOWLEDGE_BASE.get(fault_type)
            if entry:
                results.append(entry.to_dict())

        # If no keyword match, return all non-normal entries
        if not results:
            for fault_type, entry in KNOWLEDGE_BASE.items():
                if fault_type != "Normal":
                    # Check if symptom words appear in description or causes
                    text = entry.description.lower() + " ".join(c.lower() for c in entry.possible_causes)
                    if any(word in text for word in symptom_lower.split() if len(word) > 3):
                        results.append(entry.to_dict())

        return results
