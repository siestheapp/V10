struct FitRange: Codable, Identifiable {
    let id: Int
    let userId: Int
    let measurementTypeId: Int
    
    struct Range: Codable {
        let min: Double
        let max: Double
    }
    
    let goodFit: Range
    let tightFit: Range
    let looseFit: Range
    let absolute: Range
    
    enum CodingKeys: String, CodingKey {
        case id
        case userId = "user_id"
        case measurementTypeId = "measurement_type_id"
        case goodFitMin = "good_fit_min"
        case goodFitMax = "good_fit_max"
        case tightFitMin = "tight_fit_min"
        case tightFitMax = "tight_fit_max"
        case looseFitMin = "loose_fit_min"
        case looseFitMax = "loose_fit_max"
        case absoluteMin = "absolute_min"
        case absoluteMax = "absolute_max"
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(Int.self, forKey: .id)
        userId = try container.decode(Int.self, forKey: .userId)
        measurementTypeId = try container.decode(Int.self, forKey: .measurementTypeId)
        
        goodFit = Range(
            min: try container.decode(Double.self, forKey: .goodFitMin),
            max: try container.decode(Double.self, forKey: .goodFitMax)
        )
        tightFit = Range(
            min: try container.decode(Double.self, forKey: .tightFitMin),
            max: try container.decode(Double.self, forKey: .tightFitMax)
        )
        looseFit = Range(
            min: try container.decode(Double.self, forKey: .looseFitMin),
            max: try container.decode(Double.self, forKey: .looseFitMax)
        )
        absolute = Range(
            min: try container.decode(Double.self, forKey: .absoluteMin),
            max: try container.decode(Double.self, forKey: .absoluteMax)
        )
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(id, forKey: .id)
        try container.encode(userId, forKey: .userId)
        try container.encode(measurementTypeId, forKey: .measurementTypeId)
        
        try container.encode(goodFit.min, forKey: .goodFitMin)
        try container.encode(goodFit.max, forKey: .goodFitMax)
        try container.encode(tightFit.min, forKey: .tightFitMin)
        try container.encode(tightFit.max, forKey: .tightFitMax)
        try container.encode(looseFit.min, forKey: .looseFitMin)
        try container.encode(looseFit.max, forKey: .looseFitMax)
        try container.encode(absolute.min, forKey: .absoluteMin)
        try container.encode(absolute.max, forKey: .absoluteMax)
    }
    
    func predictFit(_ measurement: Double) -> String {
        if measurement < absolute.min {
            return "Too tight"
        } else if measurement <= tightFit.max {
            return "Tight fit"
        } else if measurement <= goodFit.max {
            return "Good fit"
        } else if measurement <= looseFit.max {
            return "Loose fit"
        } else {
            return "Too loose"
        }
    }
} 