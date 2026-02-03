const defaultCourses = [
  {
    id: "digital-linguistics",
    title: "Digital Linguistics",
    category: "Linguistics",
    doctors: "Dr. Rania Hassan • Dr. Omar Adel",
    portal: "faculty.edu/linguistics",
    facebook: "fb.com/linguistics",
    drive: "drive.google.com/alsun/linguistics",
    info:
      "Focus on corpus analysis, AI translation, and applied research. Weekly lab sessions with practical assignments and curated resources.",
    tags: ["AI translation", "Labs", "Weekly quizzes"],
    badge: "3 new",
    coverClass: "cover-one",
    icon: "🧠",
    summary: "Latest update: Lecture slides uploaded 15 minutes ago.",
    resources: "28",
    driveStatus: "On",
    posts: [
      {
        source: "Faculty Portal • 2 hours ago",
        title: "Lab 4 materials are now available",
        body:
          "Updated worksheets, audio samples, and a quick guide for this week’s lab. Notifications were sent to all enrolled students.",
      },
    ],
    notifications: [
      {
        title: "New Drive file uploaded: “Lab 4 Audio Pack”.",
        time: "5 minutes ago",
      },
    ],
  },
];

const courseGrid = document.querySelector("#course-grid");
const notificationGrid = document.querySelector("#notification-grid");
const courseTitle = document.querySelector("#course-title");
const courseSubtitle = document.querySelector("#course-subtitle");
const courseName = document.querySelector("#course-name");
const courseOverview = document.querySelector("#course-overview");
const courseDoctors = document.querySelector("#course-doctors");
const coursePortal = document.querySelector("#course-portal");
const courseFacebook = document.querySelector("#course-facebook");
const courseDrive = document.querySelector("#course-drive");
const courseTags = document.querySelector("#course-tags");
const coursePosts = document.querySelector("#course-posts");
const coursePostList = document.querySelector("#course-post-list");
const courseOpenLink = document.querySelector("#course-open-link");
const heroCourseTitle = document.querySelector("#hero-course-title");
const heroCourseBadge = document.querySelector("#hero-course-badge");
const heroCourseDoctors = document.querySelector("#hero-course-doctors");
const heroCourseResources = document.querySelector("#hero-course-resources");
const heroCourseDrive = document.querySelector("#hero-course-drive");
const heroCourseUpdate = document.querySelector("#hero-course-update");

let courses = [];

const buildCourseCard = (course) => {
  const card = document.createElement("article");
  card.className = "course-card";
  card.dataset.courseId = course.id;
  card.innerHTML = `
    <div class="course-cover ${course.coverClass ?? "cover-one"}">
      <span class="course-icon">${course.icon ?? "📘"}</span>
      <span class="course-notification">${course.badge ?? "New"}</span>
    </div>
    <div class="course-body">
      <h3>${course.title}</h3>
      <p>Responsible doctors: ${course.doctors ?? ""}</p>
      <div class="course-links">
        <span>Faculty Portal</span>
        <span>Facebook</span>
        <span>Drive</span>
      </div>
    </div>
    <div class="course-hover">
      <h4>Main Info</h4>
      <p>${course.info ?? ""}</p>
    </div>
  `;
  card.addEventListener("click", () => selectCourse(course.id));
  return card;
};

const renderCourses = () => {
  if (!courseGrid) {
    return;
  }
  courseGrid.innerHTML = "";
  courses.forEach((course) => courseGrid.appendChild(buildCourseCard(course)));
};

const renderNotifications = () => {
  if (!notificationGrid) {
    return;
  }
  notificationGrid.innerHTML = "";
  courses.forEach((course) => {
    (course.notifications ?? []).forEach((note) => {
      const card = document.createElement("div");
      card.className = "notification-card";
      card.innerHTML = `
        <h4>${course.title}</h4>
        <p>${note.title}</p>
        <span>${note.time}</span>
      `;
      notificationGrid.appendChild(card);
    });
  });
};

const renderTags = (tags) => {
  if (!courseTags) {
    return;
  }
  courseTags.innerHTML = "";
  (tags ?? []).forEach((tag) => {
    const span = document.createElement("span");
    span.textContent = tag;
    courseTags.appendChild(span);
  });
};

const renderPosts = (posts) => {
  const postContainer = coursePostList || coursePosts;
  if (!postContainer) {
    return;
  }
  postContainer.innerHTML = "";
  (posts ?? []).forEach((post) => {
    const article = document.createElement("article");
    article.className = "feed-card";
    article.innerHTML = `
      <p class="feed-source">${post.source}</p>
      <h4>${post.title}</h4>
      <p>${post.body}</p>
    `;
    postContainer.appendChild(article);
  });
};

const selectCourse = (courseId) => {
  if (!courseTitle) {
    return;
  }
  const selected = courses.find((course) => course.id === courseId) ?? courses[0];
  if (!selected) {
    return;
  }
  courseTitle.textContent = `${selected.title} — Course Page`;
  courseSubtitle.textContent = `Explore posts, links, and updates for ${selected.title}.`;
  courseName.textContent = selected.title;
  courseOverview.textContent = selected.info;
  courseDoctors.textContent = selected.doctors;
  coursePortal.textContent = selected.portal;
  courseFacebook.textContent = selected.facebook;
  courseDrive.textContent = selected.drive;
  renderTags(selected.tags);
  renderPosts(selected.posts);

  if (courseOpenLink) {
    courseOpenLink.href = `course.html?id=${selected.id}`;
  }

  if (heroCourseTitle) {
    heroCourseTitle.textContent = selected.title;
  }
  if (heroCourseBadge) {
    heroCourseBadge.textContent = selected.badge ?? "New";
  }
  if (heroCourseDoctors) {
    heroCourseDoctors.textContent = selected.doctors?.split("•").length ?? 0;
  }
  if (heroCourseResources) {
    heroCourseResources.textContent = selected.resources ?? "0";
  }
  if (heroCourseDrive) {
    heroCourseDrive.textContent = selected.driveStatus ?? "Off";
  }
  if (heroCourseUpdate) {
    heroCourseUpdate.textContent = selected.summary ?? "";
  }
};

const fetchCourses = async () => {
  try {
    const response = await fetch("/api/courses");
    if (!response.ok) {
      throw new Error("Failed to load courses");
    }
    const data = await response.json();
    courses = data;
  } catch (error) {
    courses = defaultCourses;
  }

  renderCourses();
  renderNotifications();
  if (courses.length > 0) {
    selectCourse(courses[0].id);
  }
};

const setupAdminLogin = () => {
  const loginForm = document.querySelector("#admin-login");
  const loginStatus = document.querySelector("#admin-login-status");
  const adminSections = document.querySelectorAll("[data-admin-only]");

  if (!loginForm || !loginStatus) {
    return;
  }

  const toggleAdminSections = (isVisible) => {
    adminSections.forEach((section) => {
      section.classList.toggle("is-hidden", !isVisible);
    });
  };

  toggleAdminSections(false);

  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(loginForm);
    const username = formData.get("username") ?? "";
    const password = formData.get("password") ?? "";

    try {
      const response = await fetch("/api/admin/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        loginStatus.textContent = "Access granted. Admin tools unlocked.";
        loginStatus.classList.remove("error");
        toggleAdminSections(true);
        loginStatus.dataset.adminUnlocked = "true";
        return;
      }
    } catch (error) {
      // Fall through to local error.
    }

    loginStatus.textContent = "Access denied. Please check your credentials.";
    loginStatus.classList.add("error");
    toggleAdminSections(false);
  });
};

const fetchCourseDetail = async () => {
  if (!courseTitle) {
    return;
  }
  const params = new URLSearchParams(window.location.search);
  const courseId = params.get("id");
  if (!courseId) {
    return;
  }
  try {
    const response = await fetch(`/api/courses/${courseId}`);
    if (!response.ok) {
      throw new Error("Course not found");
    }
    const course = await response.json();
    courses = [course];
    selectCourse(course.id);
  } catch (error) {
    // Leave defaults if fetch fails.
  }
};

const setupCourseForm = () => {
  const form = document.querySelector("#course-form");
  const status = document.querySelector("#course-form-status");

  if (!form || !status) {
    return;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const payload = {
      title: formData.get("title"),
      category: formData.get("category"),
      doctors: formData.get("doctors"),
      portal: formData.get("portal"),
      facebook: formData.get("facebook"),
      drive: formData.get("drive"),
      info: formData.get("info"),
      tags: (formData.get("tags") || "")
        .toString()
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean),
      badge: formData.get("badge"),
      icon: formData.get("icon"),
      coverClass: formData.get("coverClass"),
      summary: formData.get("summary"),
      resources: formData.get("resources"),
      driveStatus: formData.get("driveStatus"),
    };

    try {
      const response = await fetch("/api/courses", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Save failed");
      }

      status.textContent = "Course saved. Refreshing list...";
      status.classList.remove("error");
      await fetchCourses();
      form.reset();
    } catch (error) {
      status.textContent = "Unable to save course. Check the server connection.";
      status.classList.add("error");
    }
  });
};

const setupIntegrationTools = () => {
  const refreshButton = document.querySelector("#refresh-integrations");
  const refreshStatus = document.querySelector("#refresh-status");
  const cookiesForm = document.querySelector("#cookies-form");
  const cookiesStatus = document.querySelector("#cookies-status");
  const broadcastForm = document.querySelector("#broadcast-form");
  const broadcastStatus = document.querySelector("#broadcast-status");

  if (refreshButton && refreshStatus) {
    refreshButton.addEventListener("click", async () => {
      refreshStatus.textContent = "Refreshing integrations...";
      refreshStatus.classList.remove("error");
      try {
        const response = await fetch("/api/integrations/refresh", { method: "POST" });
        if (!response.ok) {
          throw new Error("Refresh failed");
        }
        refreshStatus.textContent = "Refresh queued. Check back shortly.";
      } catch (error) {
        refreshStatus.textContent = "Unable to trigger refresh.";
        refreshStatus.classList.add("error");
      }
    });
  }

  if (cookiesForm && cookiesStatus) {
    cookiesForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const formData = new FormData(cookiesForm);
      cookiesStatus.textContent = "Uploading cookies...";
      cookiesStatus.classList.remove("error");
      try {
        const response = await fetch("/api/integrations/facebook/upload", {
          method: "POST",
          body: formData,
        });
        if (!response.ok) {
          throw new Error("Upload failed");
        }
        cookiesStatus.textContent = "Cookies uploaded. Sync queued for the selected course.";
        await fetch("/api/integrations/facebook/sync", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ course_id: formData.get("course_id") }),
        });
      } catch (error) {
        cookiesStatus.textContent = "Unable to upload cookies.";
        cookiesStatus.classList.add("error");
      }
    });
  }

  if (broadcastForm && broadcastStatus) {
    broadcastForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const formData = new FormData(broadcastForm);
      const message = formData.get("message");
      broadcastStatus.textContent = "Sending broadcast...";
      broadcastStatus.classList.remove("error");
      try {
        const response = await fetch("/api/whatsapp/broadcast", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ message }),
        });
        if (!response.ok) {
          throw new Error("Send failed");
        }
        broadcastStatus.textContent = "Broadcast queued to WhatsApp.";
        broadcastForm.reset();
      } catch (error) {
        broadcastStatus.textContent = "Unable to send broadcast.";
        broadcastStatus.classList.add("error");
      }
    });
  }
};

if (document.querySelector("#course-grid")) {
  fetchCourses();
} else {
  fetchCourseDetail();
}
setupAdminLogin();
setupCourseForm();
setupIntegrationTools();
