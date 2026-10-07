const descriptions = document.querySelectorAll(".job-description");
const moreButtons = document.querySelectorAll(".more-button");

moreButtons.forEach((button, index) => {
    button.addEventListener("click", function() {
        descriptions[index].classList.toggle("expanded");

        if (descriptions[index].classList.contains("expanded")) {
            button.textContent = "Less";
        } else {
            button.textContent = "More";
        }
    });
});