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
        case nextStep = "next_step"
    }
}

struct FeedbackOption: Codable {
    let value: Int
    let label: String
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

