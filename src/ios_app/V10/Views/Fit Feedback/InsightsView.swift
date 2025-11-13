import SwiftUI

struct InsightsView: View {
    let insights: TryOnInsights
    let brandName: String
    let sizeTried: String
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Header with context
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text(brandName)
                                .font(.headline)
                            Text("Size \(sizeTried)")
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                        }
                        
                        Spacer()
                        
                        // Confidence badge
                        HStack(spacing: 4) {
                            Image(systemName: confidenceIcon)
                                .font(.caption)
                            Text(insights.confidence.capitalized)
                                .font(.caption)
                                .fontWeight(.medium)
                        }
                        .foregroundColor(confidenceColor)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(confidenceColor.opacity(0.15))
                        .cornerRadius(20)
                    }
                    .padding()
                    
                    // Main AI Summary
                    VStack(alignment: .leading, spacing: 12) {
                        Label("AI Analysis", systemImage: "sparkles")
                            .font(.headline)
                            .foregroundColor(.blue)
                        
                        Text(insights.summary)
                            .font(.body)
                            .fixedSize(horizontal: false, vertical: true)
                            .lineSpacing(4)
                    }
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Color.blue.opacity(0.08))
                    )
                    
                    // Key Findings (if any)
                    if !insights.keyFindings.isEmpty {
                        VStack(alignment: .leading, spacing: 12) {
                            Label("Key Findings", systemImage: "list.bullet")
                                .font(.headline)
                            
                            ForEach(insights.keyFindings, id: \.self) { finding in
                                HStack(alignment: .top, spacing: 8) {
                                    Image(systemName: "checkmark.circle.fill")
                                        .font(.caption)
                                        .foregroundColor(.green)
                                        .padding(.top, 2)
                                    
                                    Text(finding)
                                        .font(.subheadline)
                                        .fixedSize(horizontal: false, vertical: true)
                                }
                            }
                        }
                        .padding()
                    }
                    
                    // Recommendations (if any)
                    if !insights.recommendations.isEmpty {
                        VStack(alignment: .leading, spacing: 12) {
                            Label("Recommendations", systemImage: "lightbulb")
                                .font(.headline)
                                .foregroundColor(.orange)
                            
                            ForEach(insights.recommendations, id: \.self) { recommendation in
                                HStack(alignment: .top, spacing: 8) {
                                    Image(systemName: "arrow.right.circle")
                                        .font(.caption)
                                        .foregroundColor(.orange)
                                        .padding(.top, 2)
                                    
                                    Text(recommendation)
                                        .font(.subheadline)
                                        .fixedSize(horizontal: false, vertical: true)
                                }
                            }
                        }
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(Color.orange.opacity(0.08))
                        )
                    }
                    
                    // If AI is asking questions (contains "?")
                    if insights.summary.contains("?") {
                        VStack(alignment: .leading, spacing: 12) {
                            Label("The AI wants to learn more", systemImage: "questionmark.circle")
                                .font(.headline)
                                .foregroundColor(.purple)
                            
                            Text("Answer these questions in your next try-on to help personalize recommendations:")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            
                            // Extract questions from summary
                            let questions = extractQuestions(from: insights.summary)
                            ForEach(questions, id: \.self) { question in
                                HStack(alignment: .top, spacing: 8) {
                                    Text("•")
                                        .font(.headline)
                                        .foregroundColor(.purple)
                                    
                                    Text(question)
                                        .font(.subheadline)
                                        .fixedSize(horizontal: false, vertical: true)
                                }
                            }
                        }
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(Color.purple.opacity(0.08))
                        )
                    }
                    
                    // Action buttons
                    VStack(spacing: 12) {
                        Button(action: {
                            // Could save to user's notes or trigger another try-on
                            dismiss()
                        }) {
                            Label("Save & Continue Shopping", systemImage: "cart")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent)
                        
                        Button(action: {
                            dismiss()
                        }) {
                            Text("Done")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.bordered)
                    }
                    .padding(.top)
                }
                .padding()
            }
            .navigationTitle("Fit Insights")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { dismiss() }) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.secondary)
                    }
                }
            }
        }
    }
    
    private var confidenceIcon: String {
        switch insights.confidence.lowercased() {
        case "high": return "checkmark.seal.fill"
        case "medium": return "exclamationmark.triangle.fill"
        default: return "questionmark.diamond.fill"
        }
    }
    
    private var confidenceColor: Color {
        switch insights.confidence.lowercased() {
        case "high": return .green
        case "medium": return .orange
        default: return .gray
        }
    }
    
    private func extractQuestions(from text: String) -> [String] {
        // Split by question marks and filter out empty strings
        let sentences = text.components(separatedBy: "?")
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
        
        // Find sentences that look like questions
        var questions: [String] = []
        for sentence in sentences {
            // Look for question starters
            let questionStarters = ["how", "what", "did", "do", "does", "would", "could", "should", "is", "are", "was", "were"]
            let words = sentence.lowercased().components(separatedBy: " ")
            
            if let firstWord = words.first,
               questionStarters.contains(firstWord) || sentence.contains("?") {
                questions.append(sentence + "?")
            }
        }
        
        return questions
    }
}

// Preview
struct InsightsView_Previews: PreviewProvider {
    static var previews: some View {
        InsightsView(
            insights: TryOnInsights(
                summary: "Great news! J.Crew size L fits you well overall, with just slight tightness in the chest. Based on your feedback, you're between L and XL at J.Crew. How did you feel about the fabric weight? Did you like the slim cut through the body?",
                keyFindings: [
                    "Chest runs small in this style",
                    "Sleeve length is perfect for you",
                    "This matches your usual J.Crew size"
                ],
                measurementAnalysis: [:],
                recommendations: [
                    "Try XL for a more relaxed chest fit",
                    "Look for 'Classic' fit instead of 'Slim'",
                    "This brand's L works for most styles"
                ],
                confidence: "high"
            ),
            brandName: "J.Crew",
            sizeTried: "L"
        )
    }
}

