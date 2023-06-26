const form = document.getElementById("write-form");

const handleSubmitForm = async (event) => {
  // submit 이벤트는 이벤트 발생후 페이지를 자동으로 리로드하기 떄문에 이를 막아야 함.
  event.preventDefault();
  const body = new FormData(form);
  body.append("insertAt", new Date().getTime());

  try {
    const res = await fetch("/items", {
      method: "POST",
      body,
    });

    const data = await res.json();
    //루트 페이지로 이동
    if (data === "200") window.location.pathname = "/";
  } catch (error) {
    console.error("fail");
  }
};

form.addEventListener("submit", handleSubmitForm);
