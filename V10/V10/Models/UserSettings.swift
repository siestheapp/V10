import SwiftUI

class UserSettings: ObservableObject {
    @Published var useMetricSystem: Bool {
        didSet {
            UserDefaults.standard.set(useMetricSystem, forKey: "useMetricSystem")
        }
    }
    
    @Published var userEmail: String {
        didSet {
            UserDefaults.standard.set(userEmail, forKey: "userEmail")
        }
    }
    
    @Published var userId: Int {
        didSet {
            UserDefaults.standard.set(userId, forKey: "userId")
        }
    }
    
    init() {
        self.useMetricSystem = UserDefaults.standard.bool(forKey: "useMetricSystem")
        self.userEmail = UserDefaults.standard.string(forKey: "userEmail") ?? ""
        self.userId = UserDefaults.standard.integer(forKey: "userId")
    }
} 