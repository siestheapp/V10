import Foundation
import SwiftUI

// MARK: - Try-On History Models

struct TryOnHistoryItem: Codable, Identifiable {
    let id: Int
    let brand: String
    let productName: String
    let productUrl: String
    let imageUrl: String?
    let fitType: String?
    let sizeTried: String
    let colorTried: String?
    let overallFeedback: String
    let chestFeedback: String?
    let waistFeedback: String?
    let sleeveFeedback: String?
    let neckFeedback: String?
    let tryOnDate: String
    let measurements: [String: String]
    
    enum CodingKeys: String, CodingKey {
        case id
        case brand
        case productName = "product_name"
        case productUrl = "product_url"
        case imageUrl = "image_url"
        case fitType = "fit_type"
        case sizeTried = "size_tried"
        case colorTried = "color_tried"
        case overallFeedback = "overall_feedback"
        case chestFeedback = "chest_feedback"
        case waistFeedback = "waist_feedback"
        case sleeveFeedback = "sleeve_feedback"
        case neckFeedback = "neck_feedback"
        case tryOnDate = "try_on_date"
        case measurements
    }
    
    // Computed property for formatted date - DATE ONLY, user's timezone
    var formattedDate: String {
        guard let date = ISO8601DateFormatter().date(from: tryOnDate) else {
            return tryOnDate
        }
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .none  // DATE ONLY, no time
        formatter.timeZone = TimeZone.current  // User's current timezone
        return formatter.string(from: date)
    }
    
    // Computed property for feedback summary
    var feedbackSummary: String {
        var feedbacks: [String] = []
        
        if let chest = chestFeedback, !chest.isEmpty {
            feedbacks.append("Chest: \(chest)")
        }
        if let waist = waistFeedback, !waist.isEmpty {
            feedbacks.append("Waist: \(waist)")
        }
        if let sleeve = sleeveFeedback, !sleeve.isEmpty {
            feedbacks.append("Sleeve: \(sleeve)")
        }
        if let neck = neckFeedback, !neck.isEmpty {
            feedbacks.append("Neck: \(neck)")
        }
        
        return feedbacks.isEmpty ? overallFeedback : feedbacks.joined(separator: " • ")
    }
    
    // Computed property for feedback color
    var feedbackColor: Color {
        switch overallFeedback.lowercased() {
        case "good fit", "perfect":
            return .green
        case "tight but i like it", "loose but i like it":
            return .orange
        case "too tight", "too loose", "too big":
            return .red
        default:
            return .gray
        }
    }
    
    // Computed property for feedback emoji
    var feedbackEmoji: String {
        switch overallFeedback.lowercased() {
        case "good fit", "perfect":
            return "✅"
        case "tight but i like it":
            return "🤏"
        case "loose but i like it":
            return "👌"
        case "too tight":
            return "😖"
        case "too loose", "too big":
            return "😮"
        default:
            return "❓"
        }
    }
}
