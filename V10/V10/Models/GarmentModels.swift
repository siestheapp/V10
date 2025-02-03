import Foundation

struct UniqloGarment: Codable {
    let id: String
    let name: String
    let brand: String
    let size: String
    let category: String
    let subcategory: String
    let color: String
    let price: Double
    let imageUrl: String
    let productUrl: String
}

// Create a new model for flexible measurements
struct MeasurementValue: Codable {
    let value: String
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        value = try container.decode(String.self)
    }
}

// Request model for sending scan data to server
struct GarmentRequest: Codable {
    let product_code: String
    let scanned_size: String?
    let scanned_price: Double?
}

// Models for handling measurements
struct SizeMeasurements: Codable {
    let measurements: [String: String]
    
    var bodyLength: String? { 
        measurements["body_length"] ?? measurements["body_length_back"] 
    }
    var bodyWidth: String? { 
        measurements["body_width"] 
    }
    var sleeveLength: String? { 
        measurements["sleeve_length"] 
    }
    var shoulderWidth: String? { 
        measurements["shoulder_width"] 
    }
    
    var allMeasurements: [String: String] { 
        measurements 
    }
}

struct Measurements: Codable {
    let units: String
    let sizes: [String: SizeMeasurements]
}

// Response model from server
struct GarmentResponse: Codable {
    let id: String
    let name: String
    let category: String
    let measurements: Measurements?
    let imageUrl: String?
    let productUrl: String?
}

// Model for OCR extracted data
struct ExtractedGarmentInfo {
    var productCode: String?
    var name: String?
    var size: String?
    var color: String?
    var price: Double?
    var materials: [String: Double]
    var measurements: [String: Double]
    var rawText: String?
} 