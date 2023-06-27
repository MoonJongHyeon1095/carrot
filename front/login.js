const form = document.querySelector("#login-form");

const handleSubmit = async (event) => {
  event.preventDefault();
  const formData = new FormData(form);

  //sha256은 단방향. 즉, 복호화가 불가능. 따라서 이렇게 암호화를 한 것 끼리 비교해야 한다.
  //회원가입시 암호화하여 저장하고, 로그인시에도 암호화하여 암호문끼리 비교하는 것.
  //같은 평문을 암호화하면 암호문도 같기 때문에, 비교가 가능하다.
  const sha256Password = sha256(formData.get("password"));
  formData.set("password", sha256Password);

  const res = await fetch("/login", {
    method: "post",
    body: formData,
  });
  const data = await res.json();
  console.log(data);
  const accessToken = data.access_token;
  if (accessToken) {
    localStorage.setItem("token", accessToken);
    window.location.pathname = "/";
  }

  // //   모든 아이템 리스트 조회
  // console.log(accessToken);
  // const res2 = await fetch("/items", {
  //   headers: {
  //     Authorization: "Bearer " + accessToken,
  //   },
  // });
  // const data2 = await res2.json();
  // console.log(data2);

  // if (res.status === 200) {
  //   alert("로그인에 성공했습니다!");
  //   window.location.pathname = "/";
  // } else if (res.status === 401) {
  //   alert("id 혹은 password가 틀렸습니다.");
  // }
};

form.addEventListener("submit", handleSubmit);
