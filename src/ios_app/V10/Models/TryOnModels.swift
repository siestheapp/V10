import Foundation

// MARK: - Try-On Session Models

struct TryOnSession: Codable {
    let sessionId: String
    let brand: String
    let brandId: Int
    let productName: String
    let productUrl: String
    let productImage: String
    let availableMeasurements: [String]
    let feedbackOptions: [FeedbackOption]
    let sizeOptions: [String]
    let fitOptions: [String]
    let colorOptions: [JCrewColor]
    let currentColor: String
    let nextStep: String
    
    enum CodingKeys: String, CodingKey {
        case sessionId = "session_id"
        case brand
        case brandId = "brand_id"
        case productName = "product_name"
        case productUrl = "product_url"
        case productImage = "product_image"
        case availableMeasurements = "available_measurements"
        case feedbackOptions = "feedback_options"
        case sizeOptions = "size_options"
        case fitOptions = "fit_options"
        case colorOptions = "color_options"
        case currentColor = "current_color"
        case nextStep = "next_step"
    }
}

struct FeedbackOption: Codable {
    let value: Int
    let label: String
}

// MARK: - Color Models

struct JCrewColor: Codable, Hashable {
    let name: String
    let code: String?
    let productCode: String?
    let imageUrl: String?
    let hex: String?
    
    init(name: String, code: String? = nil, productCode: String? = nil, imageUrl: String? = nil, hex: String? = nil) {
        self.name = name
        self.code = code
        self.productCode = productCode
        self.imageUrl = imageUrl
        self.hex = hex
    }
    
    enum CodingKeys: String, CodingKey {
        case name
        case code
        case productCode
        case imageUrl
        case hex
    }
    
    init(from decoder: Decoder) throws {
        // Support decoding from either a string (legacy) or an object (rich)
        let container = try? decoder.singleValueContainer()
        if let name = try? container?.decode(String.self) {
            self.name = name
            self.code = nil
            self.productCode = nil
            self.imageUrl = nil
            self.hex = nil
            return
        }
        let keyed = try decoder.container(keyedBy: CodingKeys.self)
        self.name = (try? keyed.decode(String.self, forKey: .name)) ?? ""
        self.code = try? keyed.decodeIfPresent(String.self, forKey: .code)
        self.productCode = try? keyed.decodeIfPresent(String.self, forKey: .productCode)
        self.imageUrl = try? keyed.decodeIfPresent(String.self, forKey: .imageUrl)
        self.hex = try? keyed.decodeIfPresent(String.self, forKey: .hex)
    }
}

// MARK: - Try-On Response Models

struct TryOnResponse: Codable {
    let garmentId: Int
    let status: String
    let insights: TryOnInsights
    let feedbackStored: [FeedbackStored]
    let message: String
    
    enum CodingKeys: String, CodingKey {
        case garmentId = "garment_id"
        case status
        case insights
        case feedbackStored = "feedback_stored"
        case message
    }
}

struct TryOnInsights: Codable {
    let summary: String
    let keyFindings: [String]
    let measurementAnalysis: [String: String]
    let recommendations: [String]
    let confidence: String
    
    enum CodingKeys: String, CodingKey {
        case summary
        case keyFindings = "key_findings"
        case measurementAnalysis = "measurement_analysis"
        case recommendations
        case confidence
    }
}

struct FeedbackStored: Codable {
    let dimension: String
    let rating: Int
    let feedbackText: String
    
    enum CodingKeys: String, CodingKey {
        case dimension
        case rating
        case feedbackText = "feedback_text"
    }
}

