// scripts.js

document.addEventListener("DOMContentLoaded", function () {
    // Example function to change button color on click
    var buttons = document.querySelectorAll("button");
    buttons.forEach(function (button) {
        button.addEventListener("click", function () {
            button.style.backgroundColor = "#ff8b3d";
        });
    });

    // Additional JavaScript functionality can be added here
});
