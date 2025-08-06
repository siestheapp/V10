// SizeRecommendationScreen.swift
// Premium size recommendation screen inspired by Lyst, MrPorter, TikTok
// Full-screen, information-dense layout with proper screen real estate usage

import SwiftUI

struct SizeRecommendationScreen: View {
    let recommendation: SizeRecommendationResponse
    @Environment(\.dismiss) private var dismiss
    
    // Get confidence tier info with fallback
    private var confidenceInfo: ConfidenceTier {
        recommendation.confidenceTier ?? ConfidenceTier(
            tier: "fair",
            confidenceScore: recommendation.confidence,
            label: "Good Fit",
            icon: "✅",
            color: "green",
            description: "This should work for you"
        )
    }
    
    var body: some View {
        ScrollView {
            VStack(spacing: 0) {
                // HERO SECTION - Inspired by MrPorter product pages
                VStack(spacing: 20) {
                    // Brand header
                    HStack {
                        Button("Close") { dismiss() }
                            .foregroundColor(.blue)
                        Spacer()
                        Text(recommendation.brand.uppercased())
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.secondary)
                            .letterSpacing(1.2)
                    }
                    .padding(.horizontal, 20)
                    
                    // MAIN RECOMMENDATION - Full width, premium styling
                    VStack(spacing: 16) {
                        // Confidence + Size - Lyst-style prominence
                        HStack(alignment: .center, spacing: 20) {
                            // Confidence icon - large and prominent
                            Text(confidenceInfo.icon)
                                .font(.system(size: 40))
                            
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Size \(recommendation.recommendedSize)")
                                    .font(.system(size: 48, weight: .bold))
                                    .foregroundColor(.primary)
                                
                                Text(confidenceInfo.label)
                                    .font(.title2)
                                    .fontWeight(.medium)
                                    .foregroundColor(getConfidenceColor())
                            }
                            
                            Spacer()
                        }
                        
                        // KEY INSIGHT - TikTok-style scannable info
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Why this size works for you")
                                .font(.headline)
                                .foregroundColor(.primary)
                            
                            // Measurement analysis - information dense
                            VStack(spacing: 8) {
                                MeasurementRow(
                                    dimension: "Chest", 
                                    status: .perfect,
                                    detail: "42\" fits your 40-44\" preference perfectly"
                                )
                                
                                MeasurementRow(
                                    dimension: "Neck", 
                                    status: .perfect,
                                    detail: "16\" fits your 16-16.5\" zone comfortably"
                                )
                                
                                MeasurementRow(
                                    dimension: "Sleeve", 
                                    status: .perfect,
                                    detail: "34\" fits your 33.5-36\" range ideally"
                                )
                            }
                        }
                        
                        // REFERENCE GARMENTS - Lyst-style "Similar to items you own"
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Based on your closet")
                                .font(.headline)
                                .foregroundColor(.primary)
                            
                            VStack(spacing: 6) {
                                ReferenceGarmentRow(
                                    brand: "J.Crew",
                                    item: "Cotton crewneck sweater",
                                    size: "L",
                                    match: "Same size, similar fit"
                                )
                                
                                ReferenceGarmentRow(
                                    brand: "Theory",
                                    item: "Button-down shirt",
                                    size: "M", 
                                    match: "Good chest match"
                                )
                            }
                        }
                    }
                    .padding(.horizontal, 20)
                }
                .padding(.vertical, 20)
                .background(
                    RoundedRectangle(cornerRadius: 0)
                        .fill(Color(.systemBackground))
                )
                
                // ALTERNATIVES SECTION - eBay-style specific feedback
                VStack(alignment: .leading, spacing: 16) {
                    Text("Other sizes")
                        .font(.title2)
                        .fontWeight(.semibold)
                        .foregroundColor(.primary)
                        .padding(.horizontal, 20)
                    
                    VStack(spacing: 12) {
                        AlternativeSizeRow(
                            size: "M",
                            status: .notRecommended,
                            reason: "Chest too tight",
                            detail: "38-40\" vs your 40-44\" preference",
                            impact: "Will feel snug across chest"
                        )
                        
                        AlternativeSizeRow(
                            size: "XL", 
                            status: .notRecommended,
                            reason: "Too loose overall",
                            detail: "44-46\" vs your 40-44\" preference", 
                            impact: "Will feel baggy and loose"
                        )
                    }
                    .padding(.horizontal, 20)
                }
                .padding(.vertical, 24)
                .background(Color(.systemGray6))
                
                // ACTION SECTION
                VStack(spacing: 16) {
                    // Primary CTA - Premium styling
                    Button(action: {
                        // Add to closet action
                    }) {
                        HStack {
                            Text(confidenceInfo.icon)
                                .font(.title3)
                            Text("Add Size \(recommendation.recommendedSize) to Closet")
                                .font(.headline)
                                .fontWeight(.semibold)
                        }
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 16)
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(getConfidenceColor())
                        )
                    }
                    
                    // Secondary actions
                    HStack(spacing: 12) {
                        Button("View Size Guide") {
                            // Size guide action
                        }
                        .font(.subheadline)
                        .foregroundColor(.blue)
                        
                        Spacer()
                        
                        Button("Need Help?") {
                            // Help action  
                        }
                        .font(.subheadline)
                        .foregroundColor(.blue)
                    }
                }
                .padding(.horizontal, 20)
                .padding(.vertical, 24)
            }
        }
        .navigationBarHidden(true)
    }
    
    private func getConfidenceColor() -> Color {
        switch confidenceInfo.color.lowercased() {
        case "green": return .green
        case "orange": return .orange  
        case "red": return .red
        case "blue": return .blue
        default: return .green
        }
    }
}

// MARK: - Supporting Views

struct MeasurementRow: View {
    let dimension: String
    let status: MeasurementStatus
    let detail: String
    
    var body: some View {
        HStack(spacing: 12) {
            // Status indicator
            Image(systemName: status.icon)
                .foregroundColor(status.color)
                .font(.system(size: 16, weight: .semibold))
                .frame(width: 20)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(dimension)
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .foregroundColor(.primary)
                
                Text(detail)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
        }
        .padding(.vertical, 4)
    }
}

struct ReferenceGarmentRow: View {
    let brand: String
    let item: String
    let size: String
    let match: String
    
    var body: some View {
        HStack(spacing: 12) {
            Circle()
                .fill(.blue.opacity(0.2))
                .frame(width: 8, height: 8)
            
            VStack(alignment: .leading, spacing: 2) {
                HStack(spacing: 4) {
                    Text(brand)
                        .font(.subheadline)
                        .fontWeight(.medium)
                    Text("Size \(size)")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                
                Text(item)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            Text(match)
                .font(.caption)
                .foregroundColor(.blue)
        }
        .padding(.vertical, 2)
    }
}

struct AlternativeSizeRow: View {
    let size: String
    let status: MeasurementStatus
    let reason: String
    let detail: String
    let impact: String
    
    var body: some View {
        HStack(alignment: .top, spacing: 16) {
            // Size badge
            VStack {
                Text(size)
                    .font(.title3)
                    .fontWeight(.bold)
                    .foregroundColor(.primary)
                    .frame(width: 40, height: 40)
                    .background(
                        Circle()
                            .fill(Color(.systemGray5))
                    )
                
                Image(systemName: status.icon)
                    .foregroundColor(status.color)
                    .font(.caption)
            }
            
            VStack(alignment: .leading, spacing: 4) {
                Text(reason)
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .foregroundColor(.primary)
                
                Text(detail)
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Text(impact)
                    .font(.caption)
                    .foregroundColor(.orange)
                    .italic()
            }
            
            Spacer()
        }
        .padding(.vertical, 8)
    }
}

enum MeasurementStatus {
    case perfect, good, concern, notRecommended
    
    var icon: String {
        switch self {
        case .perfect: return "checkmark.circle.fill"
        case .good: return "checkmark.circle"
        case .concern: return "exclamationmark.triangle"
        case .notRecommended: return "xmark.circle"
        }
    }
    
    var color: Color {
        switch self {
        case .perfect: return .green
        case .good: return .blue
        case .concern: return .orange
        case .notRecommended: return .red
        }
    }
}

#Preview {
    SizeRecommendationScreen(
        recommendation: SizeRecommendationResponse(
            productUrl: "https://jcrew.com/example",
            brand: "J.Crew",
            analysisType: "comprehensive",
            dimensionsAnalyzed: ["chest", "neck", "sleeve"],
            referenceGarments: [:],
            recommendedSize: "L",
            recommendedFitScore: 0.92,
            confidence: 0.95,
            reasoning: "Perfect match",
            primaryConcerns: [],
            comprehensiveAnalysis: true,
            allSizes: [],
            confidenceTier: ConfidenceTier(
                tier: "excellent",
                confidenceScore: 0.95,
                label: "Great Fit",
                icon: "✅",
                color: "green",
                description: "Perfect match"
            ),
            humanExplanation: "Perfect match across 3 measurements",
            alternativeExplanations: []
        )
    )
}