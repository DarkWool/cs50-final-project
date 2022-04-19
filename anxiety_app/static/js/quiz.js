const test = (function () {
    let container = document.getElementById("questionContainer");
    let data = new FormData();
    let next = document.getElementById("next");
    let inputs;
    
    // Get the current parameter of the actual window - (if no parameter is provided '1' will be assigned)
    const QUESTIONS = parseInt(document.getElementById("counter_number").dataset.total);
    let currQuery = new URLSearchParams(window.location.search);
    let currQuestion = currQuery.get("question") ?? 1;

    function _appendFormData() {
        let options = document.getElementsByName(`question${currQuestion}`);
        let value;

        for (option of options) {
            // Get the value of the answer selected by the user
            if (option.checked) {
                value = option.value;
                break;
            }
        }

        // Each time a question gets answered append the value of the answer on a FormData object
        data.set(`question${currQuestion}`, value);
    }

    async function _fetchQuestions() {
        _detachEvents();
        _appendFormData();

        // Check if there is another question, if not you can post the data to the server.
        currQuestion++;
        if (currQuestion > QUESTIONS) {
            return _postData();
        }

        // Fetch the next question data (template) from the server
        let url = `${location.pathname}?question=${currQuestion}`;
        let response = await fetch(`${url}`, {
            method: "POST"
        });

        if (response.ok) {
            return _render(await response.text());
        }
    }

    async function _postData() {
        let post = await fetch("/anxiety-test/results", {
            method: "POST",
            body: data
        });

        let postRes = await post.json();
        return window.location.href = postRes.url;
    }

    function _enableNextBtn(el) {
        next.disabled = false;

        for (input of inputs) {
            input.classList.remove("selected");
        }
        el.target.classList.add("selected")
    }

    function _attachEvents() {
        next = document.getElementById("next");
        next.disabled = true;
        next.addEventListener("click", _fetchQuestions);

        inputs = document.querySelectorAll("input[type='radio']");
        for (input of inputs) {
            input.addEventListener("input", _enableNextBtn);
            input.disabled = false;
        }
    }

    function _detachEvents() {
        next.removeEventListener("click", _fetchQuestions);

        for (input of inputs) {
            input.removeEventListener("input", _enableNextBtn);
        }
    }

    function _render(template) {
        container.innerHTML = template;
        _attachEvents();
    }

    _attachEvents();
})();