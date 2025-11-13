// For Uniqlo product scanning
struct Product: Codable {
    let id: String
    let brand: String
    let name: String
    let size: String
    let price: Double
    let measurements: ProductMeasurements  // Renamed to avoid conflict
    let productUrl: String?
    let imageUrl: String?
}

struct ProductMeasurements: Codable {  // Renamed from Measurements
    let chest: String?
    let length: String?
    let sleeve: String?
}

// For size guide data (if still needed)
struct SizeGuideData: Codable {  // Renamed from MeasurementsData
    let units: String
    let measurement_type: String?
    let sizes: [String: SizeData]
}

struct SizeData: Codable {
    let body_length_back: String
    let body_width: String
    let sleeve_length: String
    let shoulder_width: String
} 