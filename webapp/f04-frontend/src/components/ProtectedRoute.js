import React from "react";
import { Redirect } from "@reach/router";
import { isAuthenticated } from "../services/auth";

export const ProtectedRoute = ({ component: Component, ...rest }) => {
  if (isAuthenticated()) {
    return <Component {...rest} />;
  } else {
    return <Redirect from={rest.path} to={"/login/0"} noThrow />;
  }
};

export default ProtectedRoute;
