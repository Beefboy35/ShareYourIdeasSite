async function GetRegForm() {
  try {
    window.location.href = "/register";
  } catch (e) {
    console.error("Error navigating to register:", e);
    alert("Error navigating to registration page.");
  }
}

async function GetLogInForm() {
  try {
    window.location.href = "/login";
  } catch (e) {
    console.error("Error navigating to login:", e);
    alert("Error navigating to login page.");
  }
}

async function toggleSidebar() {
  const sidebar = document.querySelector('.sidebar');
  sidebar.classList.toggle('visible');
}


async function getProfile() {
  try {
    const response = await fetch("/users/action", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    if (response.status == 200) {
        data = await response.json()
      alert(`Status: ${data.message}`)
      window.location.href = "/profile";
      return;
    } else {
      alert("sign up or sign in to continue")
    }
  } catch (e) {
    console.error("Error", e)
    alert("Something went wrong(")
  }
}

async function getIdeasByDescr() {
  const dataInput = document.getElementById("ideaInput");
  const description = dataInput.value.trim(); // Crucial: Trim whitespace

  if (!description) {
    console.error("Input field is empty. Please enter a description.");
    alert("Input field is empty. Please enter a description.")
    return;
  }

  try {
    const response = await fetch(`/ideas/get_ideas_by_description/${description}`);
    if (response.status == 404) {
      alert("Sign in to continue")
      window.location.href = "/login";
      return;
    }
    if (!response.ok) {
      const errorData = await response.json();
      let message = `HTTP error! status: ${response.status}, detail: Nothing has been found`;
      console.error(message);
      alert(message);
      return;
    }
    const data = await response.json();


    displayIdeas(data);
  } catch (error) {
    console.error("Error fetching data:", error);
    alert("An error occurred while fetching data.");
  }
}


async function displayIdeas(ideas) {
  const ideaBlock = document.getElementById("ideaBlock");
  ideaBlock.innerHTML = "";
  ideas.forEach(idea => {
    const ideaDiv = document.createElement("div");
    ideaDiv.classList.add("idea-block-style")
    ideaDiv.innerHTML =
      `<p><strong>Title:</strong> ${idea.title}</p>
    <p><strong>Description:</strong> ${idea.description}</p>
    <p><strong>Time of creation:</strong> ${idea.created_at}</p>
    <p><strong>Author's nickname:</strong> ${idea.nickname}</p>`;
    ideaBlock.appendChild(ideaDiv);
  });
}

async function createIdeaButton() {
  try {
    const response = await fetch("/users/action", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      }
    })
    if (response.status != 200) {
      alert("Sign up or sign in to continue")
      return;
    }

    const model = document.querySelectorAll(".ideas-background")[0];
    const closeButton = document.querySelectorAll(".close-button")[0];
    model.style.display = "block";
    closeButton.addEventListener("click", () => {
      model.style.display = "none";
    });
  } catch (e) {
    console.error("Error", e)
    alert("something went wrong(")
  }
}

const titleInput = document.querySelectorAll(".title-input")[0];
const descriptionInput = document.querySelectorAll(".description-input")[0];
const createButton = document.querySelectorAll(".create-idea")[0];
const result = document.querySelectorAll(".result")[0];
createButton.addEventListener("click", async () => {
  result.textContent = "";
  const title = titleInput.value.trim();
  const description = descriptionInput.value.trim();
  if (!title || !description) {
    console.error("Invalid data")
    result.textContent = "Please enter title and description";
    return;
  }
  ideaData = { title, description };
  try {
    const response = await fetch("ideas/add_idea", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(ideaData),
    })
    if (!response.ok) {
      const errorData = await response.json();
      let errorMessage = `Error adding idea: ${response.status}`;
      if (errorData && errorData.message) {
        errorMessage += ` - ${errorData.message}`;
      }
      console.error(errorMessage);
      result.textContent = errorMessage;
      return;
    }
    const data = await response.json();
    console.log("Idea added:", data);
    result.textContent = "Idea added successfully!";
    titleInput.value = "";
    descriptionInput.value = "";
  } catch (e) {
    console.error("Error", e)
    alert("Something went wrong(")
  }
});


async function updateIdeaButton() {
  try {
    const response = await fetch("/users/action", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      }
    })
    if (response.status != 200) {
      alert("Sign up or sign in to continue")
      return;
    }
    const model = document.querySelectorAll(".ideas-background")[1];
    const closeButton = document.querySelectorAll(".close-button")[1];
    model.style.display = "block";
    closeButton.addEventListener("click", () => {
      model.style.display = "none";
    });
  } catch (e) {
    console.error("Error", e)
    alert("something went wrong(")
  }
}

const titleInput2 = document.querySelectorAll(".title-input")[1];
const descriptionInput2 = document.querySelectorAll(".description-input")[1];
const createButton2 = document.querySelectorAll(".create-idea")[1];
const result2 = document.querySelectorAll(".result")[1];
createButton2.addEventListener("click", async () => {
  result2.textContent = "";
  const title = titleInput2.value.trim();
  const description = descriptionInput2.value.trim();
  if (!title || !description) {
    console.error("Invalid data")
    result2.textContent = "Please enter title and description";
    return;
  }
  ideaData = { title, description };
  try {
    const response = await fetch("ideas/update_idea", {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(ideaData),
    })
    if (!response.ok) {
      const errorData = await response.json();
      let errorMessage = `Error adding idea: ${response.status}`;
      if (response.status == 404) {
        result2.textContent = "Error: This idea doesn't belong to you or doesn't exist";
        console.error(errorMessage);
        return;
      }
      if (response.status == 401) {
        alert("Please sign in to continue");
        console.error(errorMessage);
        window.location.href = "/";
        return;
      }

      if (errorData && errorData.message) {
        errorMessage += ` - ${errorData.message}`;
      }
      console.error(errorMessage);
      result2.textContent = errorMessage;
      return;
    }
    const data = await response.json();
    console.log("Idea updated:", data);
    result2.textContent = "Idea updated successfully!";
    titleInput2.value = "";
    descriptionInput2.value = "";
  } catch (e) {
    console.error("Error", e)
    alert("Something went wrong(")
  }
});

async function deleteIdeaButton() {
  try {
    const response = await fetch("users/action", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (response.status != 200) {
      alert("Sign up or sign in to continue")
      return;
    }
    const model = document.querySelectorAll(".ideas-background")[2];
    const closeButton = document.querySelectorAll(".close-button")[2];
    model.style.display = "block";
    closeButton.addEventListener("click", () => {
      model.style.display = "none";
    });
  } catch (e) {
    console.error("Error", e)
    alert("something went wrong(")
  }
}


const titleInput3 = document.querySelectorAll(".title-input")[2];
const createButton3 = document.querySelectorAll(".create-idea")[2];
const result3 = document.querySelectorAll(".result")[2];

createButton3.addEventListener("click", async () => {
  result3.textContent = ""
  const title = titleInput3.value.trim();
  if (!title) {
    console.error("Invalid data");
    result3.textContent = "Please enter title";
    return;
  }
  try {
    const response = await fetch(`ideas/delete_idea/${title}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) {
      const errorData = await response.json();
      let errorMessage = `Error deleting idea: ${response.status}`;
      if (response.status == 404) {
        result3.textContent = "Error: This idea doesn't belong to you or doesn't exist";
        console.error(errorMessage);
        return;
      }
      if (response.status == 401) {
        alert("Please sign in to continue");
        console.error(errorMessage);
        window.location.href = "/";
        return;
      }

      if (errorData && errorData.message) {
        errorMessage += ` - ${errorData.message}`;
      }
      console.error(errorMessage);
      result3.textContent = errorMessage;
      return;
    }
    const data = await response.json();
    console.log("Idea deleted:", data);
    result3.textContent = "Idea deleted successfully!";
    titleInput3.value = "";
  } catch (e) {
    console.error("Error", e)
    alert("Something went wrong(")
  }
});

async function forAdmins() {
  try {
    const response = await fetch("users/action", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (response.status != 200) {
      alert("Sign up or sign in to continue")
      return;
    }
    const rights = await fetch("ideas/all_ideas", {
      method: "GET",
      headers: {
        "Content-Type": "application/json"
      }
    })
    if (rights.status == 403) {
      alert("You have no relevant rights")
      return;
    }
    const model = document.querySelectorAll(".ideas-background")[3];
    const closeButton = document.querySelectorAll(".close-button")[4];
    model.style.display = "block";
    closeButton.addEventListener("click", () => {
      model.style.display = "none";
    });
    const result4 = document.querySelectorAll(".result")[3];
    getAllButton = document.querySelectorAll(".create-idea")[3];


    getAllButton.addEventListener("click", async () => {
      result4.innerHTML = ""
      const response = await fetch("ideas/all_ideas", {
        method: "GET",
        headers: {
          "Content-Type": "application/json"
        }
      })
      if (response.status == 403) {
        alert("You have no relevant rights")
        return;
      }
      const data = await response.json()
      const ideasBlock = document.querySelectorAll(".ideas-background")[4];
      ideasBlock.style.display = "block";
      data.forEach(idea => {
        const ideaDiv = document.createElement("div")
        ideaDiv.classList.add("idea-block-style")
        ideaDiv.innerHTML =
          `<p><strong>Title:</strong> ${idea.title}</p>
    <p><strong>Description:</strong> ${idea.description}</p>
    <p><strong>Time of creation:</strong> ${idea.created_at}</p>
    <p><strong>Author's id:</strong> ${idea.user_id}</p>
    <p><strong>Author's nickname:</strong> ${idea.nickname}</p>`;
        result4.appendChild(ideaDiv)
      });

    })
  } catch (e) {
    console.error("Error", e)
    alert("something went wrong(")
  }
}
closeButton = document.querySelectorAll(".close-button")[3];
const ideasBlock = document.querySelectorAll(".ideas-background")[4];
closeButton.addEventListener("click", async () => {
  ideasBlock.style.display = "none";
})
deleteAllButton = document.querySelectorAll(".create-idea")[4];
deleteAllButton.addEventListener("click", async () => {
  const message = document.querySelector(".message");
  message.textContent = "";
  try {
    const response = await fetch("ideas/delete_all", {
      method: "GET",
      headers: {
        "Content-Type": "application/json"
      }
    })
    if (response.status == 403) {
      alert("You have no relevant rights")
      return;
    }
    message.textContent = "All ideas have been deleted successfully";
  } catch (e) {
    console.error("Error", e);
    message.textContent = "something went wrong(";
  }
})

async function LogOut() {
  try {
    const response = await fetch("/users/logout", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    const result = await response.json()
    if (response.ok) {
      window.location.href = "/";
    } else {
      alert(result.message || 'Unknown error');
    }
  } catch (error) {
    console.error("Error", error);
    alert('Error while logging out. Please try again.');
  }
}