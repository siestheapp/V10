import Foundation

struct MeasurementRange: Codable {
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
    
    // Convert to ClosedRange<Double>
    var asRange: ClosedRange<Double> {
        min...max
    }
}

struct BrandMeasurement: Identifiable, Codable {
    let id = UUID()
    let brand: String
    let garmentName: String
    let value: Double
    let chestRange: String?
    let size: String
    let ownsGarment: Bool
    let fitType: String
    let feedback: String
}

struct MeasurementResponse: Codable {
    let measurementType: String?
    let preferredRange: MeasurementRange
    let measurements: [BrandMeasurement]
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

struct MeasurementSummary: Identifiable {
    let id = UUID()
    let name: String
    let measurements: [BrandMeasurement]
    let preferredRange: MeasurementRange
}

struct PreferredRange: Codable {
    let min: Double
    let max: Double
}

struct MeasurementData: Codable {
    let brand: String
    let garmentName: String
    let value: Double
    let size: String
    let ownsGarment: Bool
    let fitType: String
    let feedback: String
}

// New model to match server response
struct FitZoneResponse: Codable {
    let tops: FitZoneRanges
    
    enum CodingKeys: String, CodingKey {
        case tops = "Tops"
    }
}

struct FitZoneRanges: Codable {
    let tightRange: MeasurementRange
    let goodRange: MeasurementRange
    let relaxedRange: MeasurementRange
    let garments: [GarmentMeasurement]
    
    enum CodingKeys: String, CodingKey {
        case tightRange
        case goodRange
        case relaxedRange
        case garments
    }
}

struct GarmentMeasurement: Codable {
    let brand: String
    let garmentName: String
    let chestRange: String?
    let chestValue: Double
    let size: String
    let fitFeedback: String
    let feedback: String
}