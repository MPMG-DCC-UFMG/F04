import { useEffect, useState } from "react";
import routes from "../../routes";
import { Menu, Button, Icon } from "semantic-ui-react";
import { useNavigate } from "@reach/router";
import eventBus from "../../services/eventBus";
import api from "../../services/api";

export const NavBar = () => {
  const navigate = useNavigate();
  const activeItem = "home";
  const [currentUser, setCurrentUser] = useState({});
  const logout = () => navigate(routes.logout);
  const openSearch = () => {
    eventBus.dispatch("searchOpen", { message: "search!" });
  };
  useEffect(() => {
    eventBus.on("unauth", () => {
      navigate(`/login/0/?noactivity`);
    });
  });

  return (
    <Menu size="mini" inverted>
      <Menu.Item
        name="home"
        icon="home"
        active={activeItem === "home"}
        onClick={() => navigate(routes.home)}
      />

      <Menu.Item
        name="Twitter"
        icon="user"
        active={activeItem === "tweets"}
        onClick={() => navigate(routes.home)}
      />

      {/* <Menu.Item name={`Usuario: ${currentUser.email}`} icon="twitter" /> */}

      <Menu.Menu position="right">
        <Menu.Item>
          <Button color="teal" onClick={() => openSearch()}>
            <Icon name="search" /> buscar
          </Button>
          <Button color="red" onClick={() => logout()}>
            <Icon name="log out" />
            Sair
          </Button>
        </Menu.Item>
      </Menu.Menu>
    </Menu>
  );
};
