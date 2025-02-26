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
    
    init() {
        self.useMetricSystem = UserDefaults.standard.bool(forKey: "useMetricSystem")
        self.userEmail = UserDefaults.standard.string(forKey: "userEmail") ?? ""
    }
} 