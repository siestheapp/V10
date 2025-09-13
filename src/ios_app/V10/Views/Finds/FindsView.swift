import SwiftUI

struct FindsView: View {
    @State private var selectedTab: FindsTab = .all
    
    enum FindsTab: String, CaseIterable {
        case all = "All"
        case tryOns = "Try-Ons"
        
        var icon: String {
            switch self {
            case .all:
                return "list.bullet"
            case .tryOns:
                return "tshirt"
            }
        }
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Tab Pills
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    ForEach(FindsTab.allCases, id: \.self) { tab in
                        TabPill(
                            title: tab.rawValue,
                            icon: tab.icon,
                            isSelected: selectedTab == tab
                        ) {
                            selectedTab = tab
                        }
                    }
                }
                .padding(.horizontal)
            }
            .padding(.vertical, 12)
            .background(Color(.systemBackground))
            
            // Content
            TabView(selection: $selectedTab) {
                AllFindsView()
                    .tag(FindsTab.all)
                
                TryOnHistoryView()
                    .tag(FindsTab.tryOns)
            }
            .tabViewStyle(PageTabViewStyle(indexDisplayMode: .never))
        }
        .navigationTitle("Finds")
        .navigationBarTitleDisplayMode(.large)
    }
}

struct TabPill: View {
    let title: String
    let icon: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 6) {
                Image(systemName: icon)
                    .font(.caption)
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.medium)
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 8)
            .background(
                isSelected ? Color.blue : Color(.systemGray5)
            )
            .foregroundColor(
                isSelected ? .white : .primary
            )
            .clipShape(Capsule())
        }
        .buttonStyle(PlainButtonStyle())
    }
}

#Preview {
    NavigationView {
        FindsView()
    }
}

