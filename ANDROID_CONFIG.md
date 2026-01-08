# Android App - API Configuration Guide

## The Challenge

You have two backends:
- **Laptop**: `https://laptop.tyrelparker.dev` (portable, when traveling)
- **Homelab**: `https://homelab.tyrelparker.dev` (always-on, primary)

Your Android app needs to connect to whichever is available/preferred.

## Solution Options

### Option 1: Settings Toggle (Simplest)

Let the user manually select which endpoint to use.

```kotlin
// ApiConfig.kt
object ApiConfig {
    const val LAPTOP_URL = "https://laptop.tyrelparker.dev/location-tracker"
    const val HOMELAB_URL = "https://homelab.tyrelparker.dev/location-tracker"
    
    fun getBaseUrl(context: Context): String {
        val prefs = context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
        return prefs.getString("api_endpoint", HOMELAB_URL) ?: HOMELAB_URL
    }
    
    fun setBaseUrl(context: Context, url: String) {
        val prefs = context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
        prefs.edit().putString("api_endpoint", url).apply()
    }
}

// In your settings screen
RadioButton options:
○ Homelab (Recommended)
○ Laptop
```

**Pros:** Simple, reliable, user has full control
**Cons:** Manual switching required

---

### Option 2: Auto-Failover (Smart)

Try primary endpoint, automatically fall back to secondary.

```kotlin
// ApiService.kt
class ApiService(private val context: Context) {
    
    private val endpoints = listOf(
        "https://homelab.tyrelparker.dev/location-tracker",  // Try homelab first
        "https://laptop.tyrelparker.dev/location-tracker"     // Fall back to laptop
    )
    
    private var activeEndpoint: String? = null
    
    suspend fun getActiveEndpoint(): String {
        // Use cached endpoint if available
        activeEndpoint?.let { return it }
        
        // Test each endpoint
        for (endpoint in endpoints) {
            try {
                val response = withTimeout(3000) {
                    // Quick health check
                    makeRequest("$endpoint/health")
                }
                if (response.isSuccessful) {
                    activeEndpoint = endpoint
                    return endpoint
                }
            } catch (e: Exception) {
                Log.d("ApiService", "Endpoint $endpoint unavailable: ${e.message}")
            }
        }
        
        // If all fail, default to homelab
        return endpoints[0]
    }
    
    suspend fun postLocation(deviceId: String, lat: Double, lon: Double) {
        val endpoint = getActiveEndpoint()
        // ... make the POST request
    }
}
```

**Pros:** Automatic, smart, best user experience
**Cons:** Adds network overhead, might delay first request

---

### Option 3: Hybrid (Recommended)

Combine both approaches:
1. User sets preferred endpoint
2. Auto-failover if preferred fails

```kotlin
object ApiConfig {
    const val LAPTOP_URL = "https://laptop.tyrelparker.dev"
    const val HOMELAB_URL = "https://homelab.tyrelparker.dev"
    
    enum class Endpoint {
        HOMELAB, LAPTOP, AUTO
    }
    
    fun getEndpointPreference(context: Context): Endpoint {
        val prefs = context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
        val pref = prefs.getString("endpoint_preference", "AUTO")
        return Endpoint.valueOf(pref ?: "AUTO")
    }
}

class ApiService(private val context: Context) {
    
    suspend fun getActiveEndpoint(): String {
        return when (ApiConfig.getEndpointPreference(context)) {
            Endpoint.LAPTOP -> tryEndpoint(ApiConfig.LAPTOP_URL) ?: ApiConfig.HOMELAB_URL
            Endpoint.HOMELAB -> tryEndpoint(ApiConfig.HOMELAB_URL) ?: ApiConfig.LAPTOP_URL
            Endpoint.AUTO -> tryEndpoint(ApiConfig.HOMELAB_URL) ?: tryEndpoint(ApiConfig.LAPTOP_URL) ?: ApiConfig.HOMELAB_URL
        }
    }
    
    private suspend fun tryEndpoint(url: String): String? {
        return try {
            withTimeout(2000) {
                val response = makeHealthCheck(url)
                if (response.isSuccessful) url else null
            }
        } catch (e: Exception) {
            null
        }
    }
}

// Settings UI
○ Homelab (Preferred) - Falls back to laptop if unavailable
○ Laptop (Preferred) - Falls back to homelab if unavailable
○ Auto - Tries homelab first, then laptop
```

**Pros:** Best of both worlds
**Cons:** Most complex to implement

---

## Recommended Implementation

For a learning project, **start with Option 1** (Settings Toggle):

1. Add a simple settings screen with radio buttons
2. Save preference to SharedPreferences
3. Use preference when making API calls

**Later, add Option 3** (Hybrid) when you want to learn about:
- Coroutines and timeouts
- Network error handling
- Health check endpoints
- User preference management

---

## Testing Each Mode

```bash
# Test laptop endpoint
curl https://laptop.tyrelparker.dev/location-tracker/health

# Test homelab endpoint
curl https://homelab.tyrelparker.dev/location-tracker/health

# Simulate homelab down (stop docker-compose on homelab)
# Your app should either:
# - Show error (Option 1)
# - Switch to laptop (Option 2/3)
```

---

## Pro Tip: Build Variants

For development, you can also use Gradle build variants:

```gradle
// app/build.gradle
android {
    buildTypes {
        debug {
            buildConfigField "String", "API_URL", "\"http://192.168.1.100:5000\""
        }
        release {
            buildConfigField "String", "API_URL", "\"https://homelab.tyrelparker.dev\""
        }
    }
}
```

Then in code:
```kotlin
val apiUrl = BuildConfig.API_URL
```

This separates dev (direct IP) from production (domain).

---

## Next Steps

1. Start with manual settings toggle
2. Test with both endpoints
3. Add auto-failover later as an enhancement
4. Consider adding connection status indicator in UI
