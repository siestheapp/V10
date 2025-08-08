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
    let brand: String
    let garmentName: String
    let value: Double
    let chestRange: String?
    let size: String
    let ownsGarment: Bool
    let fitType: String
    let feedback: String
    
    // Computed property for SwiftUI ForEach (not encoded/decoded)
    var id: String { "\(brand)-\(size)-\(chestRange ?? "")" }
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

// MARK: - Comprehensive Measurement Models
struct ComprehensiveMeasurementResponse: Codable {
    let tops: ComprehensiveMeasurementData
    
    // Custom coding keys to match backend response
    enum CodingKeys: String, CodingKey {
        case tops = "Tops"  // Backend sends "Tops" (capitalized)
    }
}

struct ComprehensiveMeasurementData: Codable {
    let chest: DimensionData?
    let neck: DimensionData?
    let sleeve: DimensionData?
}

struct DimensionData: Codable {
    let tightRange: MeasurementRange?
    let goodRange: MeasurementRange
    let relaxedRange: MeasurementRange?
    let garments: [GarmentData]
}

struct GarmentData: Codable, Identifiable {
    let brand: String
    let garmentName: String
    let range: String
    let value: Double?
    let size: String
    let fitFeedback: String
    let feedback: String
    let ownsGarment: Bool
    
    // Computed property for SwiftUI ForEach (not encoded/decoded)
    var id: String { "\(brand)-\(size)-\(range)" }
    
    // Custom coding keys to match API response
    enum CodingKeys: String, CodingKey {
        case brand, size, range, value, feedback
        case garmentName = "garmentName"
        case fitFeedback = "fitFeedback"
        case ownsGarment = "ownsGarment"
    }
}