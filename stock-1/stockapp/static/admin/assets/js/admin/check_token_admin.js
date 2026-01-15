async function checkToken() {
    const admin_token = localStorage.getItem('admin_token');
    const currentUrl = window.location.pathname + window.location.search;

    if (!admin_token) {
        alert('Bạn chưa đăng nhập');
        window.location.href = `/ad/login?redirect=${encodeURIComponent(currentUrl)}`;
        return;
    }

    try {
        const response = await fetch('/ad/api/check-token/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${admin_token}`
            }
        });
        const data = await response.json();
        if (!data.success) {
            alert('Hết phiên sử dụng. Vui lòng đăng nhập lại.');
            window.location.href = `/ad/login?redirect=${encodeURIComponent(currentUrl)}`;
        }
    } catch (error) {
        alert(error.message);
        window.location.href = `/ad/login?redirect=${encodeURIComponent(currentUrl)}`;
    }
}

checkToken();
console.log('Checked');
