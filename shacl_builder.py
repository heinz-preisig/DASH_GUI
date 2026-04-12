#!/usr/bin/env python3
"""
SHACL Component Library Builder
Builds basic SHACL shapes and composes them into domain frameworks
"""

from rdflib import Graph, Namespace, RDF, RDFS, XSD, Literal, URIRef
from typing import Dict, List, Optional
import uuid

# Namespaces
SH = Namespace("http://www.w3.org/ns/shacl#")
DASH = Namespace("http://datashapes.org/dash#")
EX = Namespace("http://example.org/")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

class SHACLComponentBuilder:
    """Builds basic SHACL shape components"""
    
    def __init__(self):
        self.graph = Graph()
        self.components = {}
    
    def create_property_shape(self, path: str, name: str, datatype: str = None, 
                            min_count: int = 0, max_count: int = None,
                            description: str = None, editor: str = None,
                            node_kind: str = None, class_constraint: str = None) -> URIRef:
        """Create a basic SHACL property shape"""
        prop_id = URIRef(f"{path}Property")
        
        # Add property shape
        self.graph.add((prop_id, RDF.type, SH.PropertyShape))
        self.graph.add((prop_id, SH.path, URIRef(path)))
        self.graph.add((prop_id, SH.name, Literal(name)))
        
        if datatype:
            self.graph.add((prop_id, SH.datatype, URIRef(datatype)))
        
        if min_count > 0:
            self.graph.add((prop_id, SH.minCount, Literal(min_count)))
        
        if max_count:
            self.graph.add((prop_id, SH.maxCount, Literal(max_count)))
        
        if description:
            self.graph.add((prop_id, SH.description, Literal(description)))
        
        if editor:
            self.graph.add((prop_id, DASH.editor, URIRef(editor)))
        
        if node_kind:
            self.graph.add((prop_id, SH.nodeKind, URIRef(node_kind)))
        
        if class_constraint:
            self.graph.add((prop_id, SH["class"], URIRef(class_constraint)))
        
        return prop_id
    
    def create_node_shape(self, shape_class: str, properties: List[URIRef],
                        target_class: str = None, description: str = None) -> URIRef:
        """Create a SHACL node shape from properties"""
        shape_id = URIRef(f"{EX}{shape_class}Shape")
        
        # Add node shape
        self.graph.add((shape_id, RDF.type, SH.NodeShape))
        self.graph.add((shape_id, RDFS.label, Literal(f"{shape_class} Shape")))
        
        if target_class:
            self.graph.add((shape_id, SH.targetClass, URIRef(target_class)))
        
        if description:
            self.graph.add((shape_id, SH.description, Literal(description)))
        
        # Add properties
        for prop in properties:
            self.graph.add((shape_id, SH.property, prop))
        
        return shape_id
    
    def get_person_component(self) -> URIRef:
        """Create basic Person shape component"""
        if "Person" not in self.components:
            name_prop = self.create_property_shape(
                f"{EX}fullName", "Full Name", XSD.string, 
                min_count=1, description="Person's full name"
            )
            
            email_prop = self.create_property_shape(
                f"{EX}email", "Email", XSD.string,
                description="Person's email address"
            )
            
            birthdate_prop = self.create_property_shape(
                f"{EX}birthDate", "Birth Date", XSD.date,
                description="Person's birth date"
            )
            
            person_shape = self.create_node_shape(
                "Person", [name_prop, email_prop, birthdate_prop],
                target_class=f"{EX}Person",
                description="Basic person information"
            )
            
            self.components["Person"] = person_shape
        
        return self.components["Person"]
    
    def get_organization_component(self) -> URIRef:
        """Create basic Organization shape component"""
        if "Organization" not in self.components:
            name_prop = self.create_property_shape(
                f"{EX}orgName", "Organization Name", XSD.string,
                min_count=1, description="Organization name"
            )
            
            type_prop = self.create_property_shape(
                f"{EX}orgType", "Organization Type", XSD.string,
                description="Type of organization"
            )
            
            website_prop = self.create_property_shape(
                f"{EX}website", "Website", XSD.anyURI,
                description="Organization website"
            )
            
            org_shape = self.create_node_shape(
                "Organization", [name_prop, type_prop, website_prop],
                target_class=f"{EX}Organization",
                description="Basic organization information"
            )
            
            self.components["Organization"] = org_shape
        
        return self.components["Organization"]
    
    def get_project_component(self) -> URIRef:
        """Create basic Project shape component"""
        if "Project" not in self.components:
            title_prop = self.create_property_shape(
                f"{EX}projectTitle", "Project Title", XSD.string,
                min_count=1, description="Project title"
            )
            
            description_prop = self.create_property_shape(
                f"{EX}projectDescription", "Description", XSD.string,
                description="Project description", 
                editor=str(DASH.TextAreaEditor)
            )
            
            start_date_prop = self.create_property_shape(
                f"{EX}startDate", "Start Date", XSD.date,
                description="Project start date"
            )
            
            end_date_prop = self.create_property_shape(
                f"{EX}endDate", "End Date", XSD.date,
                description="Project end date"
            )
            
            project_shape = self.create_node_shape(
                "Project", [title_prop, description_prop, start_date_prop, end_date_prop],
                target_class=f"{EX}Project",
                description="Basic project information"
            )
            
            self.components["Project"] = project_shape
        
        return self.components["Project"]
    
    def serialize(self, format: str = "turtle") -> str:
        """Serialize the SHACL graph"""
        return self.graph.serialize(format=format)


class SHACLDomainComposer:
    """Composes basic components into domain-specific frameworks"""
    
    def __init__(self, builder: SHACLComponentBuilder):
        self.builder = builder
        self.domains = {}
    
    def create_research_domain(self) -> str:
        """Create research domain framework"""
        # Get basic components
        person_shape = self.builder.get_person_component()
        org_shape = self.builder.get_organization_component()
        project_shape = self.builder.get_project_component()
        
        # Create research-specific properties
        researcher_prop = self.builder.create_property_shape(
            f"{EX}researcher", "Researcher", 
            node_kind=SH.BlankNodeOrIRI,
            class_constraint=f"{EX}Person",
            description="Researcher involved in the project"
        )
        
        funding_prop = self.builder.create_property_shape(
            f"{EX}fundingAmount", "Funding Amount", XSD.decimal,
            description="Project funding amount"
        )
        
        # Create enhanced research project shape
        research_project_shape = self.builder.create_node_shape(
            "ResearchProject", 
            [funding_prop, researcher_prop],
            target_class=f"{EX}ResearchProject",
            description="Research project with funding and researchers"
        )
        
        # Add inheritance from basic Project
        self.builder.graph.add((research_project_shape, RDFS.subClassOf, project_shape))
        
        return self.builder.serialize()
    
    def create_medical_domain(self) -> str:
        """Create medical domain framework"""
        # Get basic person component for patient
        person_shape = self.builder.get_person_component()
        
        # Create medical-specific properties
        patient_id_prop = self.builder.create_property_shape(
            f"{EX}patientId", "Patient ID", XSD.string,
            min_count=1, description="Unique patient identifier"
        )
        
        diagnosis_prop = self.builder.create_property_shape(
            f"{EX}diagnosis", "Diagnosis", XSD.string,
            description="Medical diagnosis",
            editor=str(DASH.TextAreaEditor)
        )
        
        treatment_prop = self.builder.create_property_shape(
            f"{EX}treatment", "Treatment", XSD.string,
            description="Medical treatment plan",
            editor=str(DASH.TextAreaEditor)
        )
        
        # Create patient shape
        patient_shape = self.builder.create_node_shape(
            "Patient", [patient_id_prop, diagnosis_prop, treatment_prop],
            target_class=f"{EX}Patient",
            description="Medical patient information"
        )
        
        # Add inheritance from basic Person
        self.builder.graph.add((patient_shape, RDFS.subClassOf, person_shape))
        
        return self.builder.serialize()


if __name__ == "__main__":
    # Demo: Build basic components and compose domains
    builder = SHACLComponentBuilder()
    composer = SHACLDomainComposer(builder)
    
    print("=== Basic Person Component ===")
    person_shacl = builder.get_person_component()
    print(builder.serialize())
    
    print("\n=== Research Domain Framework ===")
    research_shacl = composer.create_research_domain()
    print(research_shacl)
