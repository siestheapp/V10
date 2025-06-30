import Foundation

struct MeasurementRange {
    let min: Double
    let max: Double
    
    init(value: Double) {
        self.min = value
        self.max = value
    }
    
    init(min: Double, max: Double) {
        self.min = min
        self.max = max
    }
    
    var average: Double {
        (min + max) / 2
    }
}

struct BrandMeasurement: Identifiable {
    let id = UUID()
    let brand: String
    let garmentName: String
    let measurementRange: MeasurementRange
    let size: String
    let ownsGarment: Bool
    let fitContext: String?
    let userFeedback: String?
    let confidence: Double
}

struct MeasurementSummary: Identifiable {
    let id = UUID()
    let name: String
    let measurements: [BrandMeasurement]
    let preferredRange: MeasurementRange
}

enum FitType: String, Codable, CaseIterable {
    case tight = "Tight"
    case regular = "Regular"
    case relaxed = "Relaxed"
}

enum GarmentType: String, Codable, CaseIterable {
    case tShirt = "T-Shirt"
    case polo = "Polo"
    case buttonUp = "Button-Up"
    case sweater = "Sweater"
    case sweatshirt = "Sweatshirt"
}

struct FitFeedback: Codable {
    let brand: String
    let garmentName: String
    let size: String
    let fitType: FitType
    let garmentType: GarmentType?
    let customFeedback: String?
    
    enum CodingKeys: String, CodingKey {
        case brand
        case garmentName = "garment_name"
        case size
        case fitType = "fit_type"
        case garmentType = "garment_type"
        case customFeedback = "custom_feedback"
    }
}