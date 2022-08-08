import { createPortal } from "react-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const CustomToastContainer = () => {
  return createPortal(<ToastContainer />, document.body);
};

export default CustomToastContainer;
