import React, { useState, useEffect } from "react";
import { Button, Modal, Form, Label } from "semantic-ui-react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { registerLocale } from "react-datepicker";
import pt from "date-fns/locale/pt";
import { useForm, Controller } from "react-hook-form";
import eventBus from "../../../services/eventBus";

export const Search = () => {
  const [open, setOpen] = React.useState(false);
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);

  const {
    control,
    register,
    setValue,
    handleSubmit,
    formState: { errors },
  } = useForm();

  registerLocale("pt", pt);
  const onSubmit = (data) => {
    const hashtags = data.hashtags.split(",");

    const sanitizedHashtags = hashtags.map((v) => {
      return v.replace(/[\s#]/gm, "");
    });

    data.hashtags =
      sanitizedHashtags[0] !== "" ? "#" + sanitizedHashtags.join(", #") : "";
    localStorage.setItem("SEARCH_FILTERS", JSON.stringify(data));
    eventBus.dispatch("performSearch", JSON.stringify(data));
    setOpen(false);
  };

  const fillSearchForm = () => {
    const filters = JSON.parse(localStorage.getItem("SEARCH_FILTERS"));

    if (!filters) return;

    if (filters.startDate) {
      setStartDate(new Date(filters.startDate));
      setValue("startDate", filters.startDate);
    }
    if (filters.endDate) {
      setEndDate(new Date(filters.endDate));
      setValue("endDate", filters.endDate);
    }
    if (filters.hashtags) {
      setValue("hashtags", filters.hashtags);
    }
    if (filters.user) {
      setValue("user", filters.user);
    }

    if (filters.q) {
      setValue("q", filters.q);
    }
  };

  useEffect(() => {
    eventBus.on("searchOpen", (data) => {
      setOpen(!open);
      fillSearchForm();
    });
    fillSearchForm();
  }, [setOpen]);

  return (
    <Modal
      size="mini"
      onClose={() => {
        setOpen(false);
        setEndDate(null);
        setStartDate(null);
      }}
      onOpen={() => {
        setOpen(true);

        fillSearchForm();
      }}
      open={open}
    >
      <Modal.Header>Filtrar tweets</Modal.Header>
      <Modal.Content>
        <Modal.Description>
          <Form onSubmit={handleSubmit(onSubmit)}>
            <Form.Field>
              {errors.startDate && (
                <Label basic color="red" pointing="below">
                  Por favor, informe um data inicial.
                </Label>
              )}
              <Controller
                name="startDate"
                control={control}
                defaultValue={startDate}
                render={({
                  field: { onChange, value },
                  fieldState: { error },
                }) => (
                  <DatePicker
                    dateFormat="dd/MM/yyyy"
                    placeholderText="De"
                    selected={startDate}
                    onChange={(date) => {
                      setStartDate(date);
                      onChange(date);
                    }}
                  />
                )}
                rules={{ required: "Informe uma data." }}
              />
            </Form.Field>
            <Form.Field>
              <Controller
                name="endDate"
                control={control}
                defaultValue=""
                render={({
                  field: { onChange, value },
                  fieldState: { error },
                }) => (
                  <DatePicker
                    dateFormat="dd/MM/yyyy"
                    placeholderText="Até"
                    selected={endDate}
                    onChange={(date) => {
                      setEndDate(date);
                      onChange(date);
                    }}
                  />
                )}
              />
            </Form.Field>
            <Form.Field>
              <input
                {...register("q")}
                placeholder="Palavras-chave (e.g., eleições 2022, urna eletrônica)"
              />
            </Form.Field>
            <Form.Field>
              <input
                {...register("hashtags")}
                placeholder="Hashtags (e.g., #voto, #eleicao)"
              />
            </Form.Field>
            <Form.Field>
              <input
                {...register("user")}
                placeholder="Usuario (e.g., @user)"
              />
            </Form.Field>
            <Button
              content="Filtrar!"
              labelPosition="right"
              icon="search"
              type="submit"
              positive
            />
          </Form>
        </Modal.Description>
      </Modal.Content>
      {/* <Modal.Actions>
        <Button
          content="Filtrar!"
          labelPosition="right"
          icon="search"
          onClick={() => setOpen(false)}
          positive
          type="submit"
        />
      </Modal.Actions> */}
    </Modal>
  );
};

export default Search;
