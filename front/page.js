// export class Pagination {
//   constructor() {
//     this.currentPage = 1;
//   }

//   renderPageBtn = (startPage) => {
//     startPage ? startPage : (startPage = this.currentPage);

//     const div = document.createElement("div");
//     div.className = "pagination";

//     const pagesDiv = document.createElement("div");
//     pagesDiv.className = "pagination__pages";

//     for (let pageNum = startPage; pageNum <= startPage + 4; pageNum++) {
//       const pageBtn = document.createElement("button");
//       pageBtn.className = "pagination__page";
//       pageBtn.innerText = this.pageNum;

//       pagesDiv.appendChild(pageBtn);
//     }
//     div.appendChild(pagesDiv);
//   };

//   renderMoreBtn = () => {
//     const loadMoreBtn = document.createElement("button");
//     loadMoreBtn.className = "loadMoreBtn";
//     loadMoreBtn.addEventListener("click", () => {
//       const lastPage =
//         document.querySelectorAll(".pagination__page")[-1].innerText;
//       this.renderPageBtn(lastPage + 1);
//     });
//   };
// }

// module.exports = Pagination;
