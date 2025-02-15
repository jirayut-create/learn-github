async function checkIP() {
    const ip = document.getElementById("ipInput").value;
    const door = document.getElementById("doorInput").value;
    const resultDiv = document.getElementById("result");

    if (!ip) {
        resultDiv.innerHTML = "กรุณากรอกเลข IP";
        resultDiv.style.color = "red";
        return;
    }
    if (!door) {
        resultDiv.innerHTML = "กรุณากรอกหมายเลขประตู";
        resultDiv.style.color = "red";
        return;
    }

    try {
        const response = await fetch("/check_ip/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ip, door })  // ส่ง ip และ door ไปที่ API
        });

        const data = await response.json();

        if (response.ok) {
            resultDiv.innerHTML = data.message;
            resultDiv.style.color = data.status === "success" ? "green" : "red";
        } else {
            resultDiv.innerHTML = `❌ ${data.detail}`;
            resultDiv.style.color = "red";
        }
    } catch (error) {
        resultDiv.innerHTML = "❌ เกิดข้อผิดพลาดในการเชื่อมต่อ";
        resultDiv.style.color = "red";
    }
}

async function opendoor() {
    const door = document.getElementById("doorid").value;
    const resultDiv = document.getElementById("result");

    if (!door) {
        resultDiv.innerHTML = "กรุณากรอกหมายเลขประตู";
        resultDiv.style.color = "red";
        return;
    }

    try {
        const response = await fetch("/open_door/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({  door })  // ส่ง ip และ door ไปที่ API
        });

        const data = await response.json();

        if (response.ok) {
            resultDiv.innerHTML = data.message;
            resultDiv.style.color = data.status === "success" ? "green" : "red";
        } else {
            resultDiv.innerHTML = `❌ ${data.detail}`;
            resultDiv.style.color = "red";
        }
    } catch (error) {
        resultDiv.innerHTML = "❌ เกิดข้อผิดพลาดในการเชื่อมต่อ";
        resultDiv.style.color = "red";
    }
}