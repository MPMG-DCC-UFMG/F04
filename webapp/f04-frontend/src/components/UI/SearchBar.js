import React, { useEffect } from "react";
import {
  Checkbox,
  Grid,
  Menu,
  Segment,
  Sidebar,
  Button,
  Form,
} from "semantic-ui-react";
import eventBus from "../../services/eventBus";

const SearchBar = ({ children }) => {
  const [visible, setVisible] = React.useState(false);

  useEffect(() => {
    eventBus.on("searchOpen", (data) => setVisible(!visible));
  }, [setVisible]);

  return (
    <Grid columns={1}>
      <Grid.Column>
        <Sidebar.Pushable as={Segment}>
          <Sidebar
            as={Menu}
            animation="overlay"
            icon="labeled"
            onHide={() => setVisible(false)}
            vertical
            align="left"
            visible={visible}
          >
            <Menu.Item>
              <Form>
                <Form.Field>
                  <label>Busca</label>
                  <input placeholder="Termo de Busca" />
                </Form.Field>
                <Form.Field>
                  <label>Usuário</label>
                  <input placeholder="Digita o @ do usuário: ex. @user" />
                </Form.Field>
                <Form.Field>
                  <label>Score acima de</label>
                  <input placeholder="ex.: 0.98" />
                </Form.Field>
                <Form.Field>
                  <label>Filtrar por #hashtags</label>
                  <input placeholder="ex.: #eleicoes" />
                </Form.Field>
                <Form.Field>
                  <Checkbox label="Somente retweets" />
                </Form.Field>
                <Button type="submit" color="teal" fluid>
                  Buscar
                </Button>
              </Form>
            </Menu.Item>
          </Sidebar>

          <Sidebar.Pusher dimmed={visible}>{children}</Sidebar.Pusher>
        </Sidebar.Pushable>
      </Grid.Column>
    </Grid>
  );
};

export default SearchBar;
