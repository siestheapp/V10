// TryOnSessionModels.swift
// Models for the new try-on session flow

import Foundation

// MARK: - Try-On Session Models

struct TryOnSessionData: Codable {
    let sessionId: String
    let userId: Int
    let storeLocation: String?
    let storeBrand: String?
    let status: SessionStatus
    let createdAt: Date
    
    enum SessionStatus: String, Codable {
        case active = "active"
        case completed = "completed"
        case abandoned = "abandoned"
    }
}

struct TryOnItem: Codable, Identifiable {
    let id: Int
    let sessionId: Int
    let garmentId: Int
    let sizeTried: String
    let tryOrder: Int
    let finalDecision: FinalDecision?
    let purchaseSize: String?
    let fitScore: Double?
    let notes: String?
    
    enum FinalDecision: String, Codable {
        case bought = "bought"
        case passed = "passed"
        case pending = "pending"
        case considering = "considering"
    }
}

// MARK: - Dimension Feedback

enum FitDimension: String, CaseIterable {
    case chest = "chest"
    case neck = "neck"
    case sleeve = "sleeve"
    case waist = "waist"
    case length = "length"
    case overall = "overall"
    
    var displayName: String {
        switch self {
        case .chest: return "Chest"
        case .neck: return "Collar"
        case .sleeve: return "Sleeves"
        case .waist: return "Waist"
        case .length: return "Length"
        case .overall: return "Overall Fit"
        }
    }
    
    var questionText: String {
        switch self {
        case .chest: return "How does the CHEST fit?"
        case .neck: return "How does the COLLAR feel?"
        case .sleeve: return "How do the SLEEVES fit?"
        case .waist: return "How does the WAIST fit?"
        case .length: return "How's the LENGTH?"
        case .overall: return "How's the OVERALL fit?"
        }
    }
}

struct DimensionFeedback: Codable {
    let dimension: String
    let feedbackValue: Int
    let feedbackText: String
    let skipped: Bool
    
    static func getFeedbackText(for value: Int) -> String {
        switch value {
        case 1: return "Too Tight"
        case 2: return "Snug but Good"
        case 3: return "Perfect"
        case 4: return "Roomy but Good"
        case 5: return "Too Loose"
        default: return "Unknown"
        }
    }
    
    static func getFeedbackEmoji(for value: Int) -> String {
        switch value {
        case 1: return "😖"
        case 2: return "🤏"
        case 3: return "✅"
        case 4: return "👌"
        case 5: return "😮"
        default: return "❓"
        }
    }
}

// MARK: - API Request/Response Models

struct StartTryOnSessionRequest: Codable {
    let userId: Int
    let productUrl: String
    let storeLocation: String?
    let storeBrand: String?
}

struct StartTryOnSessionResponse: Codable {
    let sessionId: Int
    let garmentId: Int
    let brand: String
    let productName: String
    let availableSizes: [String]
    let availableDimensions: [String]
}

struct SubmitTryOnFeedbackRequest: Codable {
    let sessionId: Int
    let garmentId: Int
    let sizeTried: String
    let feedbackData: [DimensionFeedback]
    let finalDecision: String?
    let purchaseSize: String?
    let notes: String?
}

// MARK: - View State Models

class TryOnSessionState: ObservableObject {
    @Published var currentSession: TryOnSessionData?
    @Published var currentGarment: Garment?
    @Published var selectedSize: String = ""
    @Published var currentDimensionIndex: Int = 0
    @Published var feedbackValues: [FitDimension: Int] = [:]
    @Published var skippedDimensions: Set<FitDimension> = []
    @Published var isSubmitting: Bool = false
    @Published var error: String?
    @Published var availableDimensions: [FitDimension] = []
    
    var currentDimension: FitDimension? {
        // Use only available dimensions from backend, not all cases
        let dimensions = availableDimensions.isEmpty ? FitDimension.allCases.filter { $0 != .length } : availableDimensions
        guard currentDimensionIndex < dimensions.count else { return nil }
        return dimensions[currentDimensionIndex]
    }
    
    var isLastDimension: Bool {
        let dimensions = availableDimensions.isEmpty ? FitDimension.allCases.filter { $0 != .length } : availableDimensions
        return currentDimensionIndex >= dimensions.count - 1
    }
    
    var progress: Double {
        let dimensions = availableDimensions.isEmpty ? FitDimension.allCases.filter { $0 != .length } : availableDimensions
        return Double(currentDimensionIndex + 1) / Double(dimensions.count)
    }
    
    func nextDimension() {
        currentDimensionIndex += 1
    }
    
    func previousDimension() {
        if currentDimensionIndex > 0 {
            currentDimensionIndex -= 1
        }
    }
    
    func skipCurrentDimension() {
        if let dimension = currentDimension {
            skippedDimensions.insert(dimension)
        }
        nextDimension()
    }
    
    func startFeedback() {
        currentDimensionIndex = 0
        feedbackValues = [:]
        skippedDimensions = []
    }
    
    func reset() {
        currentDimensionIndex = 0
        feedbackValues = [:]
        skippedDimensions = []
        selectedSize = ""
        error = nil
        availableDimensions = []
    }
    
    func setAvailableDimensions(from measurements: [String]) {
        // Convert backend measurement names to FitDimension enum cases
        availableDimensions = measurements.compactMap { measurement in
            switch measurement.lowercased() {
            case "overall": return .overall
            case "chest": return .chest
            case "neck": return .neck
            case "sleeve": return .sleeve
            case "waist": return .waist
            case "length": return .length
            default: return nil
            }
        }
    }
    
    func getFeedbackSummary() -> [(dimension: String, feedback: String)] {
        var summary: [(dimension: String, feedback: String)] = []
        
        for dimension in FitDimension.allCases {
            if let value = feedbackValues[dimension] {
                summary.append((
                    dimension: dimension.displayName,
                    feedback: DimensionFeedback.getFeedbackText(for: value)
                ))
            } else if skippedDimensions.contains(dimension) {
                summary.append((
                    dimension: dimension.displayName,
                    feedback: "Skipped"
                ))
            }
        }
        
        return summary
    }
}
