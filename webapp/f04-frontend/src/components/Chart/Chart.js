import React, { useEffect, useState } from "react";
import { Header, Icon, Grid } from "semantic-ui-react";
import api from "../../services/api";
import PropTypes from "prop-types";
import ReactWordcloud from "react-wordcloud";
import "d3-transition";
import { select } from "d3-selection";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";
export const ChartReport = ({ navigate, tweets }) => {
  const [hashtags, setHashtags] = useState(null);
  const [topUsers, setTopUsers] = useState(null);
  const [topLinks, setTopLinks] = useState(null);
  function getCallback(callback) {
    return function (word, event) {
      const isActive = callback !== "onWordMouseOut";
      const element = event.target;
      const text = select(element);
      text
        .on("click", () => {
          if (isActive) {
            window.open(`https://twitter.com/hashtag/${word.text}`, "_blank");
          }
        })
        .transition()
        .attr("background", "white")
        .attr("font-size", isActive ? "200%" : "100%")
        .attr("text-decoration", isActive ? "underline" : "none");
    };
  }

  const callbacks = {
    getWordColor: (word) => (word.value > 50 ? "orange" : "purple"),
    getWordTooltip: (word) =>
      `A hashtag #${word.text} aparece ${word.value} vezes.`,
    onWordClick: getCallback("onWordClick"),
    onWordMouseOut: getCallback("onWordMouseOut"),
    onWordMouseOver: getCallback("onWordMouseOver"),
  };
  const getHashtagsCloud = () => {
    api.get("/tweets/hashtags/stats?top_n=50").then((json) => {
      const data = Object.keys(json.data.data).map((key) => {
        return { text: key, value: json.data.data[key] };
      });
      setHashtags(data);
    });
  };

  const getUsersStats = () => {
    api.get("/tweets/users/stats?top_n=50").then((json) => {
      setTopUsers({
        users: Object.keys(json.data.data),
        values: Object.values(json.data.data),
      });
    });
  };

  const getLinksStats = () => {
    api.get("/tweets/links/stats?top_n=50").then((json) => {
      setTopLinks({
        url: Object.keys(json.data.data),
        values: Object.values(json.data.data),
      });
    });
  };

  const options = {
    colors: ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"],
    enableTooltip: true,
    deterministic: false,
    fontFamily: "impact",
    fontSizes: [30, 80],
    fontStyle: "normal",
    fontWeight: "normal",
    padding: 1,
    rotations: 3,
    rotationAngles: [0, 90],
    scale: "sqrt",
    spiral: "archimedean",
    transitionDuration: 1000,
  };

  const usersOptions = {
    chart: {
      type: "column",
    },
    xAxis: {
      categories: topUsers ? topUsers.users : [],
      crosshair: true,
    },
    title: {
      text: "Top 50 Usuários",
    },
    series: [
      {
        name: "Tweets",
        data: topUsers ? topUsers.values : [],
      },
    ],
    yAxis: {
      min: 0,
      title: {
        text: "Número de Tweets",
      },
    },
  };

  const linksOptions = {
    chart: {
      type: "column",
    },
    xAxis: {
      categories: topLinks ? topLinks.url : [],
      crosshair: true,
    },
    title: {
      text: "Top 50 Links",
    },
    series: [
      {
        name: "Links",
        data: topLinks ? topLinks.values : [],
      },
    ],
    yAxis: {
      min: 0,
      title: {
        text: "Número de Tweets",
      },
    },
  };

  useEffect(() => {
    getHashtagsCloud();
    getUsersStats();
    getLinksStats();
  }, [setHashtags]);
  return (
    <>
      <Header as="h2">
        <Icon name="hashtag" />
        <Header.Content>
          Núvem de hashtags
          <Header.Subheader>
            Top 50 Hashtags encontradas no filtro aplicado
          </Header.Subheader>
        </Header.Content>
      </Header>
      <Grid fluid padded>
        <Grid.Column>
          {hashtags && (
            <ReactWordcloud
              words={hashtags}
              callbacks={callbacks}
              options={options}
            />
          )}
        </Grid.Column>
      </Grid>
      <Header as="h2">
        <Icon name="user" />
        <Header.Content>
          Top 50 usuários
          <Header.Subheader>
            Usuários que mais compartilharam tweets.
          </Header.Subheader>
        </Header.Content>
      </Header>
      <Grid fluid padded>
        <Grid.Column>
          {topUsers && (
            <HighchartsReact highcharts={Highcharts} options={usersOptions} />
          )}
        </Grid.Column>
      </Grid>
      <Header as="h2">
        <Icon name="chain" />
        <Header.Content>
          Top 50 Links
          <Header.Subheader>
            Links mais compartilhados nos tweets.
          </Header.Subheader>
        </Header.Content>
      </Header>
      <Grid fluid padded>
        <Grid.Column>
          {topUsers && (
            <HighchartsReact highcharts={Highcharts} options={linksOptions} />
          )}
        </Grid.Column>
      </Grid>
    </>
  );
};

ChartReport.propTypes = {
  tweets: PropTypes.array.isRequired,
};
