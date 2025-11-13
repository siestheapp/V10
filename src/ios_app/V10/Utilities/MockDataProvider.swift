import Foundation

// Mock data provider for contractor debugging
class MockDataProvider {
    static let shared = MockDataProvider()
    
    // Simulate network delay for realistic performance testing
    private let mockNetworkDelay: TimeInterval = 0.5
    
    // Mock user data
    func getMockUser() -> [String: Any] {
        return [
            "user_id": 1,
            "email": "test@example.com",
            "measurements": getMockMeasurements()
        ]
    }
    
    // Mock measurements
    func getMockMeasurements() -> [[String: Any]] {
        return [
            ["dimension": "chest", "value": 40.0, "unit": "inches"],
            ["dimension": "waist", "value": 32.0, "unit": "inches"],
            ["dimension": "sleeve", "value": 33.0, "unit": "inches"],
            ["dimension": "neck", "value": 15.5, "unit": "inches"]
        ]
    }
    
    // Mock garments - LARGE dataset for performance testing
    func getMockGarments() -> [[String: Any]] {
        var garments: [[String: Any]] = []
        
        // Generate 500+ items to test scrolling performance
        for i in 1...500 {
            garments.append([
                "garment_id": i,
                "brand": ["J.Crew", "Uniqlo", "Everlane", "Buck Mason"].randomElement()!,
                "product_name": "Test Shirt \(i)",
                "category": ["shirt", "t-shirt", "sweater", "jacket"].randomElement()!,
                "size": ["S", "M", "L", "XL"].randomElement()!,
                "fit_score": Double.random(in: 0.3...1.0),
                "image_url": "https://via.placeholder.com/300x400",
                "measurements": [
                    "chest": Double.random(in: 38...44),
                    "length": Double.random(in: 28...32),
                    "sleeve": Double.random(in: 32...35)
                ]
            ])
        }
        
        return garments
    }
    
    // Mock shop recommendations with images
    func getMockRecommendations() -> [[String: Any]] {
        var recommendations: [[String: Any]] = []
        
        // Generate 200+ recommendations for performance testing
        for i in 1...200 {
            recommendations.append([
                "product_id": i,
                "brand": ["J.Crew", "Uniqlo", "Everlane"].randomElement()!,
                "name": "Recommended Item \(i)",
                "price": Double.random(in: 29.99...199.99),
                "fit_score": Double.random(in: 0.7...1.0),
                "image_urls": [
                    "https://picsum.photos/300/400?random=\(i)",
                    "https://picsum.photos/300/400?random=\(i+1000)"
                ],
                "sizes_available": ["S", "M", "L", "XL"]
            ])
        }
        
        return recommendations
    }
    
    // Simulate async API call with delay
    func simulateAPICall<T>(returning data: T, delay: TimeInterval? = nil) async throws -> T {
        let actualDelay = delay ?? mockNetworkDelay
        try await Task.sleep(nanoseconds: UInt64(actualDelay * 1_000_000_000))
        return data
    }
}

