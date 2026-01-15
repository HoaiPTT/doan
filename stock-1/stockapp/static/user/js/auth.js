// Authentication module
class Auth {
    // Lấy user hiện tại từ localStorage hoặc gọi API xác thực
    static async getCurrentUser(forceRefresh = false) {
    try {
        const token = localStorage.getItem('token');
        if (!token) return null;

        // 🔹 Nếu có cache và không bắt buộc refresh → dùng cache
        if (!forceRefresh) {
            const cachedUser = localStorage.getItem('currentUser');
            if (cachedUser) {
                return JSON.parse(cachedUser);
            }
        }

        // 🔹 Gọi API lấy thông tin user mới nhất
        const res = await fetch('/api/userinfo/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            }
        });

        const data = await res.json();

        if (res.ok && data.success) {
            localStorage.setItem('currentUser', JSON.stringify(data.user));
            return data.user;
        } else {
            console.warn('Auth failed:', data.error);
            Auth.logout();
            return null;
        }
    } catch (err) {
        console.error('Error fetching current user:', err);
        return null;
    }
}

    // Đăng xuất
    static logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('currentUser');
        localStorage.removeItem('user_name');
        localStorage.removeItem('user_role');
        localStorage.removeItem('user_email');
    }

    // Check login nhanh
    static async requireLogin(redirect = true) {
        const user = await Auth.getCurrentUser();
        if (!user && redirect) {
            window.location.href = '/user/login/?return=' + encodeURIComponent(window.location.pathname);
        }
        return user;
    }



    
    // Check if user has specific plan
    static async hasSubscription(planName) {
    const user = await this.getCurrentUser();
    if (!user || !user.subscription) return false;

    const plans = ['basic', 'premium', 'professional'];
    const userPlanIndex = plans.indexOf(user.subscription.plan);
    const requiredPlanIndex = plans.indexOf(planName);

    return userPlanIndex >= requiredPlanIndex;
}


   static async getSubscriptionStatus() {
    const user = await this.getCurrentUser();
    if (!user || !user.subscription) return null;

    return {
        plan: user.subscription.plan,
        name: user.subscription.name,
        price: user.subscription.price,
        status: user.subscription.status,
        endDate: user.subscription.endDate,
        isActive: user.subscription.status === 'active' &&
                  (!user.subscription.endDate || new Date(user.subscription.endDate) > new Date())
    };
}
}
