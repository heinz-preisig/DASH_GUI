"""
Schema Helper Module
User-friendly guidance and explanations for non-SHACL experts
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class SchemaTemplate:
    """Pre-defined schema template for common use cases"""
    template_id: str
    name: str
    description: str
    category: str
    root_brick_type: str
    suggested_components: List[str]
    flow_type: str
    explanation: str
    use_cases: List[str]


class SchemaHelper:
    """Helper class for user-friendly schema creation"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
        self.explanations = self._initialize_explanations()
        self.tips = self._initialize_tips()
    
    def _initialize_templates(self) -> Dict[str, SchemaTemplate]:
        """Initialize common schema templates"""
        templates = {
            "person_profile": SchemaTemplate(
                template_id="person_profile",
                name="Person Profile",
                description="Complete person information with basic and contact details",
                category="Personal Data",
                root_brick_type="NodeShape",
                suggested_components=["name", "email", "phone", "address"],
                flow_type="sequential",
                explanation="A person profile schema captures basic personal information like name, contact details, and address. This is commonly used for user registration, contact management, or employee records.",
                use_cases=[
                    "User registration forms",
                    "Contact management systems",
                    "Employee records",
                    "Customer profiles"
                ]
            ),
            "product_catalog": SchemaTemplate(
                template_id="product_catalog",
                name="Product Catalog",
                description="Product information with pricing and categorization",
                category="E-commerce",
                root_brick_type="NodeShape",
                suggested_components=["product_name", "description", "price", "category"],
                flow_type="sequential",
                explanation="A product catalog schema stores product details including name, description, price, and category. Essential for e-commerce platforms and inventory management.",
                use_cases=[
                    "E-commerce websites",
                    "Inventory management",
                    "Product databases",
                    "Price comparison tools"
                ]
            ),
            "event_management": SchemaTemplate(
                template_id="event_management",
                name="Event Management",
                description="Event information with dates, location, and participants",
                category="Events",
                root_brick_type="NodeShape",
                suggested_components=["event_name", "date", "location", "organizer"],
                flow_type="sequential",
                explanation="An event management schema handles event details like name, date, location, and organizer information. Used for scheduling, booking systems, and event platforms.",
                use_cases=[
                    "Event booking systems",
                    "Calendar applications",
                    "Conference management",
                    "Meeting schedulers"
                ]
            ),
            "organization": SchemaTemplate(
                template_id="organization",
                name="Organization",
                description="Company or organization structure and details",
                category="Business",
                root_brick_type="NodeShape",
                suggested_components=["org_name", "org_type", "address", "contact"],
                flow_type="sequential",
                explanation="An organization schema captures company details including name, type, address, and contact information. Useful for business directories and company profiles.",
                use_cases=[
                    "Business directories",
                    "Company profiles",
                    "Organizational charts",
                    "Business registries"
                ]
            ),
            "simple_form": SchemaTemplate(
                template_id="simple_form",
                name="Simple Form",
                description="Basic form with title and description fields",
                category="Forms",
                root_brick_type="NodeShape",
                suggested_components=["title", "description"],
                flow_type="sequential",
                explanation="A simple form schema with just title and description fields. Perfect for basic data collection, feedback forms, or simple surveys.",
                use_cases=[
                    "Contact forms",
                    "Feedback surveys",
                    "Simple data entry",
                    "Comment systems"
                ]
            )
        }
        return templates
    
    def _initialize_explanations(self) -> Dict[str, str]:
        """Initialize explanations for SHACL concepts"""
        return {
            "schema": "A schema is like a blueprint or template for organizing information. It defines what data you want to collect and how it should be structured.",
            
            "brick": "Bricks are reusable building blocks for your schema. Think of them like LEGO pieces - each brick represents a specific type of information (like name, email, address).",
            
            "root_brick": "The root brick is the main building block of your schema. It represents the primary thing you're describing (like a Person, Product, or Event).",
            
            "component_brick": "Component bricks are additional building blocks that add more details to your root brick. For example, if your root is 'Person', components might be 'email', 'phone', 'address'.",
            
            "flow": "A flow defines how users will interact with your schema in a form or application. It breaks down the data entry into logical steps.",
            
            "sequential_flow": "Sequential flow guides users through steps one after another (Step 1 → Step 2 → Step 3). Good for forms where each step builds on the previous one.",
            
            "conditional_flow": "Conditional flow shows different steps based on user choices. Like 'If user selects 'Business', show company fields; if 'Personal', show individual fields.'",
            
            "parallel_flow": "Parallel flow lets users complete multiple steps simultaneously or in any order. Good for forms where different sections are independent.",
            
            "dynamic_flow": "Dynamic flow gives users complete freedom to navigate between steps. Users can go to any step in any order.",
            
            "node_shape": "NodeShape represents a main concept or entity (like Person, Product, Event). It's the container for related information.",
            
            "property_shape": "PropertyShape represents a specific piece of information (like name, email, price). It defines constraints on individual data fields.",
            
            "target_class": "Target class specifies what type of thing the schema describes. For example, 'schema:Person' means this schema is for people.",
            
            "property_path": "Property path specifies which piece of information this brick represents. For example, 'schema:name' means this brick stores names.",
            
            "constraints": "Constraints are rules that define what values are allowed. For example, 'email must be valid format' or 'age must be over 18'.",
            
            "shacl": "SHACL (Shapes Constraint Language) is a W3C standard for validating data. Don't worry about the technical details - just think of it as a way to define rules for your data.",
            
            "export_shacl": "Exporting to SHACL creates a file that other systems can use to validate data according to your schema rules."
        }
    
    def _initialize_tips(self) -> List[str]:
        """Initialize helpful tips for schema creation"""
        return [
            "Start with a clear idea of what information you want to collect",
            "Choose a root brick that represents your main concept (Person, Product, Event, etc.)",
            "Add component bricks for additional details you need",
            "Think about the user experience when choosing a flow type",
            "Use sequential flow for step-by-step forms",
            "Use conditional flow when different users need different information",
            "Test your schema with sample data before finalizing",
            "Give your schema a descriptive name so others can understand its purpose",
            "Add a good description to explain what the schema is for",
            "Consider who will use the schema when designing flows"
        ]
    
    def get_template(self, template_id: str) -> Optional[SchemaTemplate]:
        """Get a specific template"""
        return self.templates.get(template_id)
    
    def get_all_templates(self) -> List[SchemaTemplate]:
        """Get all available templates"""
        return list(self.templates.values())
    
    def get_templates_by_category(self, category: str) -> List[SchemaTemplate]:
        """Get templates by category"""
        return [t for t in self.templates.values() if t.category == category]
    
    def get_categories(self) -> List[str]:
        """Get all template categories"""
        categories = set(t.category for t in self.templates.values())
        return sorted(list(categories))
    
    def get_explanation(self, concept: str) -> Optional[str]:
        """Get explanation for a concept"""
        return self.explanations.get(concept)
    
    def get_random_tip(self) -> str:
        """Get a random helpful tip"""
        import random
        return random.choice(self.tips)
    
    def get_all_tips(self) -> List[str]:
        """Get all helpful tips"""
        return self.tips.copy()
    
    def suggest_components_for_root(self, root_brick_name: str) -> List[str]:
        """Suggest component bricks based on root brick"""
        suggestions = {
            "person": ["name", "email", "phone", "address", "birth_date"],
            "product": ["product_name", "description", "price", "category", "brand"],
            "event": ["event_name", "date", "time", "location", "organizer"],
            "organization": ["org_name", "org_type", "address", "phone", "website"],
            "user": ["username", "email", "password", "profile", "preferences"],
            "contact": ["name", "email", "phone", "company", "address"]
        }
        
        root_lower = root_brick_name.lower()
        for key, components in suggestions.items():
            if key in root_lower:
                return components
        
        # Default suggestions
        return ["name", "description", "created_date", "updated_date"]
    
    def explain_flow_type(self, flow_type: str) -> str:
        """Get detailed explanation of a flow type"""
        explanations = {
            "sequential": "Sequential flow guides users through steps in a fixed order. Each step must be completed before moving to the next. This is best for forms where information builds on previous steps, like multi-page registration forms.",
            
            "conditional": "Conditional flow shows different steps based on user choices or conditions. For example, if a user selects 'Business' as account type, they see company information fields; if they select 'Personal', they see individual fields. This is perfect for adaptive forms.",
            
            "parallel": "Parallel flow allows users to complete multiple steps simultaneously or in any order. Users can jump between different sections and complete them in their preferred order. Great for forms where sections are independent, like application forms.",
            
            "dynamic": "Dynamic flow gives users complete freedom to navigate between any steps. Users can start anywhere and move freely between sections. This is ideal for editing existing data or complex data management interfaces."
        }
        
        return explanations.get(flow_type, "Unknown flow type")
    
    def validate_schema_for_beginners(self, schema_name: str, root_brick_id: str, 
                                   component_brick_ids: List[str]) -> List[str]:
        """Validate schema with beginner-friendly messages"""
        issues = []
        
        if not schema_name.strip():
            issues.append("❌ Please give your schema a name so others can understand what it's for")
        
        if not root_brick_id:
            issues.append("❌ Please select a root brick - this is the main building block of your schema")
        
        if not component_brick_ids:
            issues.append("💡 Consider adding some component bricks to make your schema more useful")
        elif len(component_brick_ids) > 10:
            issues.append("💡 You have many component bricks. Consider if some could be combined or if they're all necessary")
        
        return issues
    
    def get_schema_summary_simple(self, schema_name: str, root_brick_name: str, 
                                component_count: int, flow_type: str) -> str:
        """Get a simple, user-friendly summary of the schema"""
        summary = f"📋 **{schema_name}**\n\n"
        summary += f"**Main Focus**: {root_brick_name}\n"
        summary += f"**Additional Details**: {component_count} component{'s' if component_count != 1 else ''}\n"
        summary += f"**User Experience**: {flow_type} flow\n\n"
        
        if component_count == 0:
            summary += "This is a simple schema with just the main information."
        elif component_count <= 3:
            summary += "This is a straightforward schema with a few additional details."
        elif component_count <= 6:
            summary += "This is a comprehensive schema with several additional details."
        else:
            summary += "This is a detailed schema with many additional components."
        
        return summary
