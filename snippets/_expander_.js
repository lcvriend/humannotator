var expander = document.getElementsByClassName("humannotator__expandable");
var i;

for (i = 0; i < expander.length; i++) {
    expander[i].addEventListener("click", function() {
        this.classList.toggle("humannotator__active");
        var content = this.nextElementSibling;
        if (content.style.display === "block") {
            content.style.display = "none";
        } else {
            content.style.display = "block";
        }
    });
};

var collapser = document.getElementsByClassName("humannotator__content");
var i;

for (i = 0; i < collapser.length; i++) {
    collapser[i].addEventListener("click", function() {
        this.style.display = "none";
    }
)};
