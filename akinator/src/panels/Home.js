import { Panel, PanelHeader, Header, Button, Group, Cell, Div, Avatar, Progress, Card, CardGrid, Text, Title, Spinner } from '@vkontakte/vkui';
import { useRouteNavigator } from '@vkontakte/vk-mini-apps-router';
import PropTypes from 'prop-types';
import { useState } from 'react';

export const Home = ({ id, fetchedUser }) => {
  const { photo_200, city, first_name, last_name } = { ...fetchedUser };
  const routeNavigator = useRouteNavigator();

  const [gameState, setGameState] = useState({
    sessionId: null,
    question: null,
    progression: 0,
    step: 0,
    finished: false,
    result: null,
    loading: false
  });

  const startGame = async () => {
    setGameState({ ...gameState, loading: true });
    try {
      const response = await fetch('https://vkakinator.onrender.com/start_game', { method: 'POST' });
      const data = await response.json();
      setGameState({
        sessionId: data.session_id,
        question: data.question,
        progression: data.progression,
        step: data.step,
        finished: false,
        result: null,
        loading: false
      });
    } catch (error) {
      console.error('Error starting game:', error);
      setGameState({ ...gameState, loading: false });
    }
  };

  const answerQuestion = async (answer) => {
    setGameState({ ...gameState, loading: true });
    try {
      const response = await fetch('https://vkakinator.onrender.com/answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: gameState.sessionId, answer })
      });
      const data = await response.json();
      if (data.finished) {
        setGameState({
          ...gameState,
          finished: true,
          result: data,
          loading: false
        });
      } else {
        setGameState({
          ...gameState,
          question: data.question,
          progression: data.progression,
          step: data.step,
          loading: false
        });
      }
    } catch (error) {
      console.error('Error answering:', error);
      setGameState({ ...gameState, loading: false });
    }
  };

  const goBack = async () => {
    if (gameState.step === 0) return;
    setGameState({ ...gameState, loading: true });
    try {
      const response = await fetch('https://vkakinator.onrender.com/back', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: gameState.sessionId })
      });
      const data = await response.json();
      setGameState({
        ...gameState,
        question: data.question,
        progression: data.progression,
        step: data.step,
        loading: false
      });
    } catch (error) {
      console.error('Error going back:', error);
      setGameState({ ...gameState, loading: false });
    }
  };

  return (
    <Panel id={id}>
      <PanelHeader>Akinator</PanelHeader>
      {fetchedUser && (
        <Group header={<Header size="s">Привет, {first_name}!</Header>}>
          <Cell before={photo_200 && <Avatar src={photo_200} />} subtitle={city?.title}>
            {`${first_name} ${last_name}`}
          </Cell>
        </Group>
      )}

      <Group header={<Header size="s">Игра Akinator</Header>}>
        {!gameState.sessionId ? (
          <Div>
            <Button stretched size="l" mode="primary" onClick={startGame} disabled={gameState.loading}>
              {gameState.loading ? <Spinner size="small" /> : 'Начать игру'}
            </Button>
          </Div>
        ) : gameState.finished ? (
          <Div>
            <Card mode="outline">
              <Div>
                <Title level="2" weight="bold">{gameState.result.name_proposition}</Title>
                <Text>{gameState.result.description_proposition}</Text>
                <Text>Pseudo: {gameState.result.pseudo}</Text>
                {gameState.result.photo && <img src={gameState.result.photo} alt="Character" style={{ width: '100%', maxWidth: '200px' }} />}
                <Text>{gameState.result.final_message}</Text>
              </Div>
            </Card>
            <Button stretched size="l" mode="secondary" onClick={startGame}>
              Играть снова
            </Button>
          </Div>
        ) : (
          <Div>
            <Progress value={gameState.progression} />
            <Text weight="regular" style={{ marginBottom: 16 }}>
              Вопрос {gameState.step + 1}: {gameState.question}
            </Text>
            <CardGrid size="l">
              <Button stretched size="l" mode="primary" onClick={() => answerQuestion('yes')} disabled={gameState.loading}>
                Да
              </Button>
              <Button stretched size="l" mode="primary" onClick={() => answerQuestion('no')} disabled={gameState.loading}>
                Нет
              </Button>
              <Button stretched size="l" mode="secondary" onClick={() => answerQuestion('i dont know')} disabled={gameState.loading}>
                Не знаю
              </Button>
              <Button stretched size="l" mode="secondary" onClick={() => answerQuestion('probably')} disabled={gameState.loading}>
                Вероятно
              </Button>
              <Button stretched size="l" mode="secondary" onClick={() => answerQuestion('probably not')} disabled={gameState.loading}>
                Вероятно нет
              </Button>
            </CardGrid>
            <Button stretched size="l" mode="tertiary" onClick={goBack} disabled={gameState.step === 0 || gameState.loading}>
              Назад
            </Button>
          </Div>
        )}
      </Group>
    </Panel>
  );
};
