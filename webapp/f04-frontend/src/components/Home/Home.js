import { NavBar } from "../UI/NavBar";
import React from "react";
import { useEffect, useState } from "react";
import api from "../../services/api";
import { useToast } from "../UI/Toast";
import { Icon, Header, Button, Label, Grid, Message } from "semantic-ui-react";
import ListTable from "../Home/ListTable";
import ListCard from "../Home/ListCard";
import Chart from "../Chart";
import Search from "../UI/Search";
import eventBus from "../../services/eventBus";
import { format } from "date-fns";
import Swal from "sweetalert2";
export const Home = () => {
  const [tweets, setTweets] = useState([]);
  const [n, setN] = useState(1);
  const [politicalTweet, setPoliticalTweet] = useState([]);
  const [notPoliticalTweet, setNotPoliticalTweet] = useState([]);
  const [quarantineTweet, setQuarantineTweet] = useState([]);

  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState({
    score: "down",
    retweets: "down",
  });

  const { showErrorMessage } = useToast();
  const [listType, setListType] = useState("table");
  const [filters, setFilters] = useState({});

  const getFilters = () => {
    let f = JSON.parse(localStorage.getItem("SEARCH_FILTERS"));

    if (f === null) {
      localStorage.setItem(
        "SEARCH_FILTERS",
        JSON.stringify({
          startDate: "",
          endDate: "",
          hashtags: "",
          user: "",
        })
      );
    }

    f = JSON.parse(localStorage.getItem("SEARCH_FILTERS"));

    setFilters(f);

    return f;
  };

  const loadMore = () => {
    setN(n + 1);
    getTweets(sortBy, n + 1);
  };

  const getPoliticalTweets = (n) => {
    api
      .get(`/tweets?top_n=${n * 100}&political=political`)
      .then((response) => {
        setPoliticalTweet(response.data.data);
        // setLoading(false);
      })
      .catch((err) => {
        //setLoading(false);
      });

    api
      .get(`/tweets?top_n=${n * 100}&political=nonpolitical`)
      .then((response) => {
        setNotPoliticalTweet(response.data.data);
        // setLoading(false);
      })
      .catch((err) => {
        //setLoading(false);
      });

    api
      .get(`/tweets?top_n=${n * 100}&political=quarantine`)
      .then((response) => {
        setQuarantineTweet(response.data.data);
        // setLoading(false);
      })
      .catch((err) => {
        //setLoading(false);
      });
  };
  const getTweets = (sort, n) => {
    if (sort) setSortBy(sort);
    setLoading(true);
    const _filters = getFilters();
    let query = "";

    if (_filters.startDate) {
      query += "&start_date=" + _filters.startDate;
    }

    if (_filters.endDate) {
      query += "&end_date=" + _filters.endDate;
    }

    if (_filters.hashtags) {
      query += "&hashtags=" + _filters.hashtags.replace(/[\s#]/gm, "");
    }

    if (_filters.user) {
      query += "&user=" + _filters.user;
    }

    if (_filters.q) {
      query += "&q=" + _filters.q;
    }

    if (_filters.sortBy) {
      query += "&score=" + _filters.sortBy?.score;
      query += "&retweets=" + _filters.sortBy?.retweets;
    }

    console.log(query, sortBy);

    api
      .get(`/tweets?top_n=${n * 100}${query}`)
      .then((response) => {
        setTweets(response.data.data);
        setLoading(false);
      })
      .catch((err) => {
        setLoading(false);
        showErrorMessage("Não conseguimos carregar os dados.");
        //navigate(routes.login);
      });

    getPoliticalTweets(n);
  };

  const changeListType = (_type) => {
    setListType(_type);
  };

  const deleteFilterItem = (key) => {
    const f = getFilters();

    f[key] = null;
    localStorage.setItem("SEARCH_FILTERS", JSON.stringify(f));

    getTweets(n);
  };

  const relabel = (tweetId, label, txt) => {
    let text =
      label == "political"
        ? "Você confirma que este post CONTÉM uma mensagem política de campanha antecipada?"
        : label == "nonpolitical"
        ? "Você confirma que este post NÃO CONTÉM uma mensagem política de campanha antecipada?"
        : "Você confirma que quer adicionar este post à lista de ANÁLISE?";

    if (label == null) {
      text =
        "Você tem certeza que deseja voltar este tweet para a lista padrão?";
    }
    text = `"${txt}" \n ${text}`;
    Swal.fire({
      title: "Aviso!",
      text: text,
      icon: "warning",
      showCancelButton: true,
      confirmButtonText: "SIM",
      cancelButtonText: "NÃO",
    }).then((result) => {
      if (result.isConfirmed) {
        api
          .get(`/tweets/labeling/${tweetId}/${label}`)
          .then(() => {
            Swal.fire("Dados Salvos!", "", "success");
            eventBus.dispatch("performSearch", {});
          })
          .catch(() => {
            showErrorMessage("Operação não realizada.");
          });
      }
    });
  };

  useEffect(() => {
    getTweets(sortBy, n);
    eventBus.on("performSearch", () => {
      //setTweets([]);

      getTweets(sortBy, n);
    });

    eventBus.on("tweetSortBy", (sort) => {
      //setTweets([]);

      getTweets(sort, n);
    });
  }, [setTweets]);
  return (
    <>
      <NavBar />
      <Search />

      <Header as="h2" size="large">
        <Icon name="twitter" />
        <Header.Content>
          Lista de Tweets ({listType === "table" && <span>Visão Tabular</span>}
          {listType === "list" && <span>Visão em Cartões</span>}
          {listType === "chart" && <span>Gráficos e Visualizações</span>}
          {listType === "political" && <span>potencialmente políticos</span>}
          {listType === "quarantine" && <span>em análise</span>}
          {listType === "notpolitical" && <span>não políticos</span>})
          <Header.Subheader>
            Clique em um tweet para mais detalhes.
          </Header.Subheader>
        </Header.Content>
      </Header>
      <Grid fluid padded columns="1">
        <Grid.Column fluid>
          <Button.Group>
            <Button
              icon
              labelPosition="left"
              onClick={() => changeListType("table")}
            >
              <Icon name="table" />
              Tabela
            </Button>
            <Button
              icon
              labelPosition="left"
              onClick={() => changeListType("list")}
            >
              <Icon name="grid layout" />
              Cartão
            </Button>
            <Button
              icon
              labelPosition="left"
              onClick={() => changeListType("chart")}
            >
              <Icon name="chart bar" />
              Gráficos
            </Button>
          </Button.Group>{" "}
          <Button
            icon
            color="blue"
            labelPosition="left"
            onClick={() => changeListType("quarantine")}
          >
            <Icon name="question circle" />
            Em análise ({quarantineTweet.length})
          </Button>
          <Button
            icon
            color="green"
            labelPosition="left"
            onClick={() => changeListType("political")}
          >
            <Icon name="thumbs up" />
            Político ({politicalTweet.length})
          </Button>
          <Button
            icon
            color="red"
            labelPosition="left"
            onClick={() => changeListType("notpolitical")}
          >
            <Icon name="thumbs down" />
            Não político ({notPoliticalTweet.length})
          </Button>
        </Grid.Column>

        {(filters?.startDate ||
          filters?.endDate ||
          filters?.hashtags ||
          filters?.q ||
          filters?.user) && (
          <Grid.Column fluid>
            <div>
              <strong>Filtros aplicados:</strong>
            </div>
            {filters?.startDate && (
              <Label color="teal">
                De: {format(new Date(filters?.startDate), "dd/MM/yyyy")}
                <Icon
                  name="delete"
                  onClick={() => deleteFilterItem("startDate")}
                />
              </Label>
            )}
            {filters?.endDate && (
              <Label color="teal">
                Até: {format(new Date(filters?.endDate), "dd/MM/yyyy")}
                <Icon
                  name="delete"
                  onClick={() => deleteFilterItem("endDate")}
                />
              </Label>
            )}
            {filters?.hashtags && (
              <Label color="teal">
                Hashtags: {filters?.hashtags}
                <Icon
                  name="delete"
                  onClick={() => deleteFilterItem("hashtags")}
                />
              </Label>
            )}
            {filters?.q && (
              <Label color="teal">
                Contém: {filters?.q}
                <Icon name="delete" onClick={() => deleteFilterItem("q")} />
              </Label>
            )}
            {filters?.user && (
              <Label color="teal">
                Postado por: {filters?.user}
                <Icon name="delete" onClick={() => deleteFilterItem("user")} />
              </Label>
            )}
          </Grid.Column>
        )}
      </Grid>
      <Grid fluid padded columns="1">
        <Grid.Column fluid>
          {listType === "table" && (
            <ListTable tweets={tweets} relabel={relabel} />
          )}
          {listType === "list" && (
            <ListCard tweets={tweets} relabel={relabel} />
          )}
          {listType === "chart" && <Chart tweets={tweets} />}
          {listType === "political" && (
            <ListTable tweets={politicalTweet} relabel={relabel} />
          )}
          {listType === "quarantine" && (
            <ListTable tweets={quarantineTweet} relabel={relabel} />
          )}
          {listType === "notpolitical" && (
            <ListTable tweets={notPoliticalTweet} relabel={relabel} />
          )}

          {!loading && tweets.length == 0 && (
            <Message info>
              <Message.Header>
                Nenhum registro encontrado para esta combinação de filtros!
              </Message.Header>
              <p>Ajuste os parâmetros do seu filtro.</p>
            </Message>
          )}

          <Button
            type="submit"
            color="red"
            fluid
            size="large"
            onClick={() => loadMore()}
          >
            Carregar mais registros...
          </Button>

          {!loading && tweets.length == 0 && (
            <Grid
              textAlign="center"
              style={{ height: "50vh" }}
              verticalAlign="middle"
            >
              <Grid.Column style={{ maxWidth: 450 }}>
                <Button
                  color="teal"
                  onClick={() => eventBus.dispatch("searchOpen")}
                >
                  <Icon name="search" />
                  Clique aqui para buscar registros
                </Button>
              </Grid.Column>
            </Grid>
          )}
        </Grid.Column>
      </Grid>
    </>
  );
};
