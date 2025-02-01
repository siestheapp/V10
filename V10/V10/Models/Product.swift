struct Product: Codable {
    let id: String
    let name: String
    let category: String
    let subcategory: String?
    let price: Double?
    let measurements: MeasurementsData
    let imageUrl: String
    let productUrl: String
}

struct MeasurementsData: Codable {
    let units: String
    let sizes: [String: SizeData]
}

struct SizeData: Codable {
    let body_length: String
    let body_width: String
    let sleeve_length: String
} 