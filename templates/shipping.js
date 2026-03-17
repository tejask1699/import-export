window.confirmShipment = function () {

    const form = document.getElementById("shippingForm");

    if (!form) {
        alert("❌ Shipping form not found!");
        return;
    }

    const formData = new FormData(form);

    fetch("/create-shipment", {
        method: "POST",
        body: formData
    })
    .then(response => response.text())
    .then(data => {

        console.log(data);

        if (data.toLowerCase().includes("success")) {
            alert("🎉 Shipment Confirmed Successfully!");
            form.reset();
        } 
        else {
            alert("❌ Shipment failed: " + data);
        }

    })
    .catch(error => {
        console.error(error);
        alert("❌ Server error.");
    });
}