"""
Location Extraction Module for UnityAid
Extracts geographic coordinates from natural language descriptions using NLP and geocoding.
"""

import re
import os
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass

@dataclass
class LocationInfo:
    """Structured location information extracted from text."""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    confidence: float = 0.0
    extraction_method: str = "none"
    raw_entities: List[str] = None
    
    def __post_init__(self):
        if self.raw_entities is None:
            self.raw_entities = []

class LocationExtractor:
    """Extracts location information from natural language text."""
    
    def __init__(self):
        self.geocoder = None
        self.nlp_model = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize geocoding and NLP services."""
        try:
            # Initialize geocoding service
            from geopy.geocoders import Nominatim
            self.geocoder = Nominatim(
                user_agent="UnityAid-DisasterResponse/1.0",
                timeout=10
            )
        except ImportError:
            print("Warning: geopy not available. Geocoding disabled.")
        
        try:
            # Try to load spaCy model for advanced NLP
            import spacy
            try:
                self.nlp_model = spacy.load("en_core_web_sm")
            except OSError:
                print("Warning: spaCy model 'en_core_web_sm' not found. Using basic extraction.")
                self.nlp_model = None
        except ImportError:
            print("Warning: spaCy not available. Using basic extraction.")
    
    def extract_location(self, text: str) -> LocationInfo:
        """
        Extract location information from text using multiple methods.
        
        Args:
            text: Natural language text containing location information
            
        Returns:
            LocationInfo object with extracted coordinates and metadata
        """
        if not text or not text.strip():
            return LocationInfo()
        
        # Try different extraction methods in order of sophistication
        location_info = self._extract_with_spacy(text)
        
        if location_info.confidence < 0.3:
            fallback_info = self._extract_with_patterns(text)
            if fallback_info.confidence > location_info.confidence:
                location_info = fallback_info
        
        # Attempt geocoding if we have an address but no coordinates
        if location_info.address and not location_info.latitude and self.geocoder:
            geocoded = self._geocode_address(location_info.address)
            if geocoded.latitude:
                location_info.latitude = geocoded.latitude
                location_info.longitude = geocoded.longitude
                location_info.confidence = max(location_info.confidence, 0.8)
                location_info.extraction_method += "+geocoding"
        
        return location_info
    
    def _extract_with_spacy(self, text: str) -> LocationInfo:
        """Extract locations using spaCy NLP model."""
        if not self.nlp_model:
            return LocationInfo()
        
        doc = self.nlp_model(text)
        locations = []
        
        # Extract geographic and organizational entities
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC", "ORG", "FAC"]:  # Geographic, Location, Organization, Facility
                locations.append(ent.text)
        
        if locations:
            # Use the first (most likely) location
            best_location = locations[0]
            confidence = 0.7 if len(locations) == 1 else 0.6
            
            return LocationInfo(
                address=best_location,
                confidence=confidence,
                extraction_method="spacy_nlp",
                raw_entities=locations
            )
        
        return LocationInfo()
    
    def _extract_with_patterns(self, text: str) -> LocationInfo:
        """Extract locations using regex patterns and heuristics."""
        text_lower = text.lower()
        locations = []
        confidence = 0.0
        
        # Common location patterns
        patterns = [
            # Business + Street patterns
            r'at\s+([^,\n]+(?:cvs|walgreens|walmart|target|mcdonalds|starbucks|hospital|clinic|school|university|mall|plaza|center)[^,\n]*)',
            r'at\s+([^,\n]+(?:street|st|avenue|ave|road|rd|boulevard|blvd|drive|dr|lane|ln|way|place|pl)[^,\n]*)',
            
            # Address patterns
            r'(\d+\s+[^,\n]+(?:street|st|avenue|ave|road|rd|boulevard|blvd|drive|dr|lane|ln))',
            
            # Intersection patterns
            r'(?:at|near)\s+([^,\n]+(?:and|\&|intersection)[^,\n]+)',
            
            # Landmark patterns
            r'(?:at|near)\s+([^,\n]*(?:hospital|clinic|school|university|airport|station|park|mall|center|plaza|building)[^,\n]*)',
            
            # City/Area patterns
            r'(?:in|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s*,\s*[A-Z]{2})?)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 3:  # Filter out very short matches
                    locations.append(match.strip())
                    confidence = max(confidence, 0.5)
        
        # Business name patterns
        business_keywords = [
            'cvs', 'walgreens', 'walmart', 'target', 'publix', 'winn-dixie',
            'mcdonalds', 'burger king', 'starbucks', 'dunkin',
            'hospital', 'clinic', 'urgent care', 'emergency room',
            'school', 'university', 'college', 'library',
            'mall', 'plaza', 'center', 'airport', 'station'
        ]
        
        for keyword in business_keywords:
            if keyword in text_lower:
                # Try to extract context around the keyword
                pattern = f'([^.!?]*{keyword}[^.!?]*)'
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match.strip()) > len(keyword) + 5:
                        locations.append(match.strip())
                        confidence = max(confidence, 0.4)
                break
        
        if locations:
            # Clean up and select the best location
            best_location = max(locations, key=len)  # Prefer more detailed descriptions
            return LocationInfo(
                address=best_location,
                confidence=confidence,
                extraction_method="pattern_matching",
                raw_entities=list(set(locations))  # Remove duplicates
            )
        
        return LocationInfo()
    
    def _geocode_address(self, address: str) -> LocationInfo:
        """Convert address to coordinates using geocoding service."""
        if not self.geocoder:
            return LocationInfo()
        
        try:
            # Add context for better geocoding (assuming Miami area for UnityAid)
            context_address = f"{address}, Miami-Dade County, Florida, USA"
            
            location = self.geocoder.geocode(context_address)
            if location:
                return LocationInfo(
                    latitude=location.latitude,
                    longitude=location.longitude,
                    address=location.address,
                    confidence=0.8,
                    extraction_method="geocoding"
                )
            
            # Fallback: try without context
            location = self.geocoder.geocode(address)
            if location:
                return LocationInfo(
                    latitude=location.latitude,
                    longitude=location.longitude,
                    address=location.address,
                    confidence=0.6,
                    extraction_method="geocoding_fallback"
                )
                
        except Exception as e:
            print(f"Geocoding error: {e}")
        
        return LocationInfo()
    
    def suggest_location_improvements(self, text: str) -> List[str]:
        """Suggest ways to improve location descriptions."""
        suggestions = []
        
        text_lower = text.lower()
        
        # Check for vague terms
        vague_terms = ['here', 'there', 'this place', 'that place', 'over there', 'nearby']
        if any(term in text_lower for term in vague_terms):
            suggestions.append("Try to be more specific than 'here' or 'there' - include street names or landmarks")
        
        # Check for missing details
        if len(text.split()) < 3:
            suggestions.append("Add more location details like street names, cross streets, or nearby landmarks")
        
        # Check for business names without addresses
        business_pattern = r'(cvs|walgreens|walmart|target|mcdonalds|starbucks)'
        if re.search(business_pattern, text_lower):
            if not re.search(r'\d+.*(?:street|st|avenue|ave|road|rd)', text_lower):
                suggestions.append("Include the street address or cross streets along with the business name")
        
        return suggestions

# Global instance for easy access
location_extractor = LocationExtractor()

def extract_coordinates_from_text(text: str) -> Tuple[Optional[float], Optional[float], Dict]:
    """
    Convenience function to extract coordinates from text.
    
    Returns:
        (latitude, longitude, metadata_dict)
    """
    result = location_extractor.extract_location(text)
    
    metadata = {
        'address': result.address,
        'confidence': result.confidence,
        'method': result.extraction_method,
        'entities': result.raw_entities,
        'suggestions': location_extractor.suggest_location_improvements(text)
    }
    
    return result.latitude, result.longitude, metadata

def test_location_extraction():
    """Test the location extraction with sample inputs."""
    test_cases = [
        "Someone stopped breathing at Doral CVS at 107th Street",
        "Car accident at the intersection of Biscayne Blvd and 125th Street",
        "Fire at Miami International Airport Terminal 3",
        "Medical emergency at Jackson Memorial Hospital emergency room",
        "Flooding at 1234 SW 8th Street Miami FL",
        "Person trapped at Aventura Mall near Nordstrom",
        "Gas leak reported at University of Miami campus",
        "Building collapse at downtown Miami near Bayside",
    ]
    
    print("Testing Location Extraction:")
    print("=" * 60)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. Input: '{text}'")
        lat, lon, metadata = extract_coordinates_from_text(text)
        
        if lat and lon:
            print(f"   Coordinates: ({lat:.6f}, {lon:.6f})")
            print(f"   Address: {metadata['address']}")
            print(f"   Confidence: {metadata['confidence']:.2f}")
            print(f"   Method: {metadata['method']}")
        else:
            print(f"   No coordinates found")
            print(f"   Extracted: {metadata['address'] or 'None'}")
            print(f"   Method: {metadata['method']}")
        
        if metadata['suggestions']:
            print(f"   Suggestions: {'; '.join(metadata['suggestions'])}")

if __name__ == "__main__":
    test_location_extraction()