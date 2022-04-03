/*
1. Get the button with the ID of next.
2. Append a listener, so each time the button is clicked create a new URL
and fetch contents for the new question.
*/

// Get the current parameter of the actual window - (if no parameter is provided '1' will be default)
const QUESTIONS = parseInt(document.getElementById("counter_number").dataset.total);

let currQuery = new URLSearchParams(window.location.search);
let currQuestion = currQuery.get("question") ?? 1;


let inputs;

function enableNext(el) { 
    next.disabled = false;
    for (input of inputs) {
        input.classList.remove("selected");
    }
    el.target.classList.add("selected");
};

function createListeners() {
    let next = document.getElementById("next");
    next.disabled = true;
    next.addEventListener("click", getQuestions);

    inputs = document.querySelectorAll("input[type='radio']");

    for (input of inputs) {
        input.addEventListener("input", enableNext);
    }
}

let container = document.getElementById("questionContainer");

let data = new FormData();

async function getQuestions() {
    let options = document.getElementsByName(`question${currQuestion}`);
    let value;

    for (option of options) {
        if (option.checked) {
            value = option.value;
            break;
        }
    }
    
    // Each time a question gets answered record the answer on a FormData object
    data.set(`question${currQuestion}`, value);
    
    entries = data.entries();
    for (entry of entries) {
        console.log(entry);
    }
    
    currQuestion++;

    if (currQuestion > QUESTIONS) {
        let post = await fetch("/anxiety-test", {
            method: "POST",
            body: data
        });

        let postRes = await post.json();
        return window.location.href = postRes.url;
    }

    let url = `${location.pathname}?question=${currQuestion}`;

    let response = await fetch(`${url}`, {
        method: "POST"
    });


    if (response.ok) {
        let question = replaceContents(await response.text());
    }
}

function replaceContents(page) {
    container.innerHTML = page;
    createListeners();
}

createListeners();