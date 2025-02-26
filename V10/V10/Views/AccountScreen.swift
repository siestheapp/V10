//
//  AccountScreen.swift
//  V10
//
//  This is the Account screen that replaces MatchScreen.
//

import SwiftUI

struct AccountScreen: View {
    @EnvironmentObject var userSettings: UserSettings
    
    var body: some View {
        NavigationView {
            List {
                // Purchases Section
                Section(header: Text("Purchases").font(.title).bold()) {
                    NavigationLink(destination: Text("Orders")) {
                        AccountRow(icon: "shippingbox", title: "Orders", subtitle: "Track orders, start a return, and more.")
                    }
                    
                    NavigationLink(destination: Text("My Closet")) {
                        AccountRow(icon: "hanger", title: "My Closet", subtitle: "View your purchased gear and sizes.")
                    }
                }
                
                // Account Section
                Section(header: Text("Account").font(.title).bold()) {
                    NavigationLink(destination: Text("Membership Benefits")) {
                        AccountRow(icon: "figure.yoga", title: "Membership Benefits", subtitle: "Explore benefits, FAQs, and events.")
                    }
                    
                    NavigationLink(destination: Text("Profile")) {
                        AccountRow(icon: "person.crop.circle", title: "Profile", subtitle: "Edit your name, email, and password.")
                    }
                }
                
                // Preferences Section
                Section(header: Text("Preferences")) {
                    Toggle("Use Metric System", isOn: $userSettings.useMetricSystem)
                    Text("Email: \(userSettings.userEmail)")
                }
                
                // Sign Out Section
                Section {
                    Button("Sign Out", role: .destructive) {
                        // Handle sign out
                    }
                }
            }
            .navigationTitle("Account")
        }
    }
}

// Reusable Row Component
struct AccountRow: View {
    let icon: String
    let title: String
    let subtitle: String
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(.black)
                .frame(width: 30)
            
            VStack(alignment: .leading) {
                Text(title)
                    .font(.headline)
                Text(subtitle)
                    .font(.subheadline)
                    .foregroundColor(.gray)
            }
        }
        .padding(.vertical, 5)
    }
}
