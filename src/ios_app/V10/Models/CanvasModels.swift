import Foundation
import SwiftUI

// MARK: - Canvas Response Models

struct CanvasResponse: Codable {
    let summary: CanvasSummary
    let rawFeedback: [FeedbackEntry]
    let bodyEstimates: [BodyEstimate]
    let fitZones: [FitZone]
    let recommendations: [RecommendationEntry]
    let algorithmDetails: AlgorithmDetails
    
    enum CodingKeys: String, CodingKey {
        case summary
        case rawFeedback = "raw_feedback"
        case bodyEstimates = "body_estimates"
        case fitZones = "fit_zones"
        case recommendations
        case algorithmDetails = "algorithm_details"
    }
}

struct CanvasSummary: Codable {
    let totalGarments: Int
    let totalFeedback: Int
    let dimensionsWithData: [String]
    let overallConfidence: Double
    let lastUpdated: String
    
    enum CodingKeys: String, CodingKey {
        case totalGarments = "total_garments"
        case totalFeedback = "total_feedback"
        case dimensionsWithData = "dimensions_with_data"
        case overallConfidence = "overall_confidence"
        case lastUpdated = "last_updated"
    }
}

struct FeedbackEntry: Codable, Identifiable {
    let id: String
    let garmentId: Int
    let brand: String
    let productName: String
    let sizeLabel: String
    let dimension: String
    let feedbackText: String
    let feedbackDate: String
    let confidence: Double
    
    enum CodingKeys: String, CodingKey {
        case id
        case garmentId = "garment_id"
        case brand
        case productName = "product_name"
        case sizeLabel = "size_label"
        case dimension
        case feedbackText = "feedback_text"
        case feedbackDate = "feedback_date"
        case confidence
    }
}

struct BodyEstimate: Codable {
    let dimension: String
    let estimatedMeasurement: Double
    let confidence: Double
    let dataPoints: Int
    let method: String
    let confidenceRange: CanvasMeasurementRange
    let details: BodyEstimateDetails
    
    enum CodingKeys: String, CodingKey {
        case dimension
        case estimatedMeasurement = "estimated_measurement"
        case confidence
        case dataPoints = "data_points"
        case method
        case confidenceRange = "confidence_range"
        case details
    }
}

// Using existing MeasurementRange from MeasurementModels.swift
// Create a type alias to avoid confusion
typealias CanvasMeasurementRange = MeasurementRange

struct BodyEstimateDetails: Codable {
    let garmentSources: [GarmentSource]
    let feedbackDistribution: [String: Int]
    let algorithmNotes: String
    
    enum CodingKeys: String, CodingKey {
        case garmentSources = "garment_sources"
        case feedbackDistribution = "feedback_distribution"
        case algorithmNotes = "algorithm_notes"
    }
}

struct GarmentSource: Codable {
    let brand: String
    let productName: String
    let size: String
    let measurement: Double
    let feedback: String
    let weight: Double
    
    enum CodingKeys: String, CodingKey {
        case brand
        case productName = "product_name"
        case size
        case measurement
        case feedback
        case weight
    }
}

struct FitZone: Codable {
    let dimension: String
    let tightMin: Double
    let tightMax: Double
    let goodMin: Double
    let goodMax: Double
    let relaxedMin: Double
    let relaxedMax: Double
    let confidence: Double
    let dataPoints: Int
    let calculationMethod: String
    
    enum CodingKeys: String, CodingKey {
        case dimension
        case tightMin = "tight_min"
        case tightMax = "tight_max"
        case goodMin = "good_min"
        case goodMax = "good_max"
        case relaxedMin = "relaxed_min"
        case relaxedMax = "relaxed_max"
        case confidence
        case dataPoints = "data_points"
        case calculationMethod = "calculation_method"
    }
}

struct RecommendationEntry: Codable {
    let brand: String
    let productName: String
    let recommendedSize: String
    let confidence: Double
    let fitScore: Double
    let reasoning: String
    let concerns: [String]
    let dimensionAnalysis: [String: DimensionAnalysis]
    
    enum CodingKeys: String, CodingKey {
        case brand
        case productName = "product_name"
        case recommendedSize = "recommended_size"
        case confidence
        case fitScore = "fit_score"
        case reasoning
        case concerns
        case dimensionAnalysis = "dimension_analysis"
    }
}

struct DimensionAnalysis: Codable {
    let fitType: String
    let score: Double
    let garmentMeasurement: Double
    let userMeasurement: Double
    let explanation: String
    
    enum CodingKeys: String, CodingKey {
        case fitType = "fit_type"
        case score
        case garmentMeasurement = "garment_measurement"
        case userMeasurement = "user_measurement"
        case explanation
    }
}

struct AlgorithmDetails: Codable {
    let bodyMeasurementEstimator: AlgorithmInfo
    let multiDimensionalAnalyzer: AlgorithmInfo
    let directGarmentComparator: AlgorithmInfo
    let fitZoneCalculator: AlgorithmInfo
    
    enum CodingKeys: String, CodingKey {
        case bodyMeasurementEstimator = "body_measurement_estimator"
        case multiDimensionalAnalyzer = "multi_dimensional_analyzer"
        case directGarmentComparator = "direct_garment_comparator"
        case fitZoneCalculator = "fit_zone_calculator"
    }
}

struct AlgorithmInfo: Codable {
    let name: String
    let version: String
    let description: String
    let parameters: [String: AlgorithmParameter]
    let confidence: Double
    let lastUpdated: String
    
    enum CodingKeys: String, CodingKey {
        case name
        case version
        case description
        case parameters
        case confidence
        case lastUpdated = "last_updated"
    }
}

struct AlgorithmParameter: Codable {
    let value: String
    let description: String
    let impact: String
}

// MARK: - Debug Models

struct DebugDimension: Identifiable {
    let id = UUID()
    let name: String
    let feedbackCount: Int
    let measurementCount: Int
    let quality: DataQuality
}

enum DataQuality: String, CaseIterable {
    case excellent = "Excellent"
    case good = "Good"  
    case fair = "Fair"
    case poor = "Poor"
    
    var color: Color {
        switch self {
        case .excellent: return .green
        case .good: return .blue
        case .fair: return .orange
        case .poor: return .red
        }
    }
    
    var threshold: Int {
        switch self {
        case .excellent: return 10
        case .good: return 6
        case .fair: return 3
        case .poor: return 0
        }
    }
}

// MARK: - Test Data for Development

extension CanvasResponse {
    static var mockData: CanvasResponse {
        CanvasResponse(
            summary: CanvasSummary(
                totalGarments: 9,
                totalFeedback: 38,
                dimensionsWithData: ["chest", "sleeve", "overall", "neck", "length"],
                overallConfidence: 0.85,
                lastUpdated: "2025-01-28T10:00:00Z"
            ),
            rawFeedback: [
                FeedbackEntry(
                    id: "1",
                    garmentId: 1,
                    brand: "Banana Republic",
                    productName: "Soft Wash Long-Sleeve T-Shirt",
                    sizeLabel: "L",
                    dimension: "chest",
                    feedbackText: "Good Fit",
                    feedbackDate: "2025-07-23T02:11:15Z",
                    confidence: 0.9
                ),
                FeedbackEntry(
                    id: "2",
                    garmentId: 1,
                    brand: "Banana Republic", 
                    productName: "Soft Wash Long-Sleeve T-Shirt",
                    sizeLabel: "L",
                    dimension: "sleeve",
                    feedbackText: "Good Fit",
                    feedbackDate: "2025-07-23T02:11:15Z",
                    confidence: 0.8
                )
            ],
            bodyEstimates: [
                BodyEstimate(
                    dimension: "chest",
                    estimatedMeasurement: 42.5,
                    confidence: 0.9,
                    dataPoints: 13,
                    method: "Weighted feedback analysis",
                    confidenceRange: CanvasMeasurementRange(min: 41.8, max: 43.2),
                    details: BodyEstimateDetails(
                        garmentSources: [
                            GarmentSource(
                                brand: "Theory",
                                productName: "Brenan Polo Shirt",
                                size: "M",
                                measurement: 41.0,
                                feedback: "Good Fit",
                                weight: 1.0
                            )
                        ],
                        feedbackDistribution: ["Good Fit": 8, "Tight but I Like It": 3, "Loose but I Like It": 2],
                        algorithmNotes: "High confidence due to consistent feedback across multiple brands"
                    )
                )
            ],
            fitZones: [
                FitZone(
                    dimension: "chest",
                    tightMin: 40.0,
                    tightMax: 41.5,
                    goodMin: 41.5,
                    goodMax: 43.5,
                    relaxedMin: 43.5,
                    relaxedMax: 45.0,
                    confidence: 0.85,
                    dataPoints: 13,
                    calculationMethod: "Statistical zones with feedback weighting"
                )
            ],
            recommendations: [],
            algorithmDetails: AlgorithmDetails(
                bodyMeasurementEstimator: AlgorithmInfo(
                    name: "Body Measurement Estimator",
                    version: "2.1",
                    description: "Converts garment feedback to body measurements",
                    parameters: [:],
                    confidence: 0.9,
                    lastUpdated: "2025-01-28T10:00:00Z"
                ),
                multiDimensionalAnalyzer: AlgorithmInfo(
                    name: "Multi-Dimensional Fit Analyzer",
                    version: "1.5",
                    description: "Analyzes fit across multiple dimensions",
                    parameters: [:],
                    confidence: 0.85,
                    lastUpdated: "2025-01-28T10:00:00Z"
                ),
                directGarmentComparator: AlgorithmInfo(
                    name: "Direct Garment Comparator",
                    version: "1.2",
                    description: "Compares garments directly",
                    parameters: [:],
                    confidence: 0.8,
                    lastUpdated: "2025-01-28T10:00:00Z"
                ),
                fitZoneCalculator: AlgorithmInfo(
                    name: "Fit Zone Calculator",
                    version: "1.0",
                    description: "Calculates statistical fit zones",
                    parameters: [:],
                    confidence: 0.75,
                    lastUpdated: "2025-01-28T10:00:00Z"
                )
            )
        )
    }
} 