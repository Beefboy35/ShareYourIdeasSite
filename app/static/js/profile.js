

async function LogOut() {
  try {
    const response = await fetch("/users/logout", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    const result = await response.json()
    if (response) {
      window.location.href = "/";
    } else {
      alert(result.message || 'Unknown error');
    }
  } catch (error) {
    console.error("Error", error);
    alert('Error while logging out. Please try again.');
  }
}

const fileInput = document.getElementById('fileInput');
const uploadForm = document.getElementById('uploadForm');
const userAva = document.getElementById('userAva');
const submitButton = document.getElementById('submitButton');
const closeButton = document.getElementById('closeButton');

function loadAvatar() {
  const storedAvatar = localStorage.getItem('avatarFilename');
  if (storedAvatar) {
    fileInput.style.display = "none";
    submitButton.style.display = "none";
    closeButton.style.display = "inline";
    const img = document.createElement('img');
    img.src = `/users/avatar/${storedAvatar}`;
    img.alt = "Uploaded Avatar";
    img.classList.add("avatar-class");
    userAva.appendChild(img);
  }
}

window.onload = function() {
  loadAvatar();
}



uploadForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    userAva.innerHTML = "";  // Clear out any existing images first

    const file = fileInput.files[0];
    if (!file) {
        alert("Please select a file")
        return;
    }
    const formData = new FormData(); // Используем форму для formData
    formData.append('file', file)

    try {
      const response = await fetch("/users/upload_ava", {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        alert(`Error: ${errorData.detail} (${response.status})`);
        return;
      }
      userAva.style.display = "inline";
      const data = await response.json();

    const img = document.createElement('img');
        img.src = `/users/avatar/${data.filename}`;  // Adjust the path if needed
        img.alt = "Uploaded Avatar";
        img.classList.add("avatar-class")
        userAva.appendChild(img);
        fileInput.style.display = "none";
        submitButton.style.display = "none";
        closeButton.style.display = "inline";
        localStorage.setItem('avatarFilename', data.filename);

    } catch (error) {
      console.error('Error:', error);
      alert('Error loading.');
    }
  });

closeButton.addEventListener("click", async () => {

  response = await fetch("users/delete_ava", {
    method: "GET",
  })
  if (response.status == 401) {
    alert("Sign in to continue")
    window.location.href = "/"
    return;
  }
  try {
    fileInput.style.display = "inline";
    submitButton.style.display = "inline";
    closeButton.style.display = "none";
    userAva.style.display = "none";
    localStorage.removeItem("avatarFilename")
    alert("Successfully deleted")
  } catch (e) {
    console.error("Error", e)
    alert("Something went wrong( Details:", e)
  }
})

async function getMain() {
  const response = await fetch("/users/action", {
    method: "POST",
    headers: {
      'Content-Type': 'application/json'
    }
  })
  if (response.status == 200) {
    window.location.href = "/";
  } else {
    window.location.href = "/";
    alert("Sign in to continue")
  }
}

async function GetMyIdeas() {
  const ideasBackground = document.querySelector(".ideas-background");
  const closeButton = document.querySelector(".close-ideas");
  if (!ideasBackground || !closeButton) {
    console.error("Elements with IDs 'ideas-background' or 'close-ideas' not found.");
    return;
  }
  try {
    const response = await fetch("/users/action", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
    });
    if (response.status == 401) {
      window.location.href = "/";
      console.error("waiting time exceeded")
      alert("waiting time exceeded. Please log in to continue");
      return;
    }
    result = document.querySelector(".result")
    result.innerHTML = "";
    ideasBackground.style.display = "block";
    closeButton.addEventListener("click", () => {
      ideasBackground.style.display = "none";
    })
    const data = await fetch("/ideas/get_user_ideas", {
      method: "GET",
      headers: {
        "Content-Type": "application/json"
      },
    });
    if (data.status == 401) {
      window.location.href = "/";
      console.error("waiting time exceeded")
      alert("waiting time exceeded. Please log in to continue");
      return;
    }
    ideas = await data.json()
    if (data.status == 404) {
        alert("User has no ideas")
        return;
    }

    ideas.forEach(idea => {
      const ideaDiv = document.createElement("div");
      ideaDiv.classList.add("idea-block-style")
      ideaDiv.innerHTML =
        `<p><strong>Title:</strong> ${idea.title}</p>
  <p><strong>Description:</strong> ${idea.description}</p>
  <p><strong>Time of creation:</strong> ${idea.created_at}</p>
  <p><strong>Author's nickname:</strong> ${idea.nickname}</p>`;
      result.appendChild(ideaDiv);
    })


  } catch (e) {
    console.error("Error", e)
    alert("Something went wrong(")
  }
}