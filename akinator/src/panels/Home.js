import { Panel, PanelHeader, Header, Button, Group, Cell, Div, Avatar, Progress, Card, CardGrid, Text, Title } from '@vkontakte/vkui';
import { useState } from 'react';

const API_BASE = 'https://vkakinator-1.onrender.com';
const REQUEST_TIMEOUT_MS = 15000;

const postJSON = async (path, body) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data?.detail || `HTTP ${response.status}`);
    }
    return data;
  } finally {
    clearTimeout(timeoutId);
  }
};

export const Home = ({ id, fetchedUser }) => {
  const { photo_200, city, first_name, last_name } = { ...fetchedUser };

  const [gameState, setGameState] = useState({
    sessionId: null,
    question: null,
    progression: 0,
    step: 0,
    finished: false,
    result: null,
    loading: false,
    error: null
  });

  const startGame = async () => {
    if (gameState.loading) return;
    setGameState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const data = await postJSON('/start_game');
      setGameState({
        sessionId: data.session_id,
        question: data.question,
        progression: data.progression,
        step: data.step,
        finished: false,
        result: null,
        loading: false,
        error: null
      });
    } catch (error) {
      console.error('Error starting game:', error);
      setGameState((prev) => ({
        ...prev,
        loading: false,
        error: 'Не удалось начать игру. Попробуйте еще раз.'
      }));
    }
  };

  const answerQuestion = async (answer) => {
    if (gameState.loading || !gameState.sessionId) return;
    setGameState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const data = await postJSON('/answer', {
        session_id: gameState.sessionId,
        answer,
        step: gameState.step
      });
      if (data.finished) {
        setGameState((prev) => ({
          ...prev,
          finished: true,
          result: data,
          loading: false,
          error: null
        }));
      } else {
        setGameState((prev) => ({
          ...prev,
          question: data.question,
          progression: data.progression,
          step: data.step,
          loading: false,
          error: null
        }));
      }
    } catch (error) {
      console.error('Error answering:', error);
      setGameState((prev) => ({
        ...prev,
        loading: false,
        error: 'Сервер отвечает слишком долго. Попробуйте снова.'
      }));
    }
  };

  const goBack = async () => {
    if (gameState.loading || gameState.step === 0 || !gameState.sessionId) return;
    setGameState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const data = await postJSON('/back', { session_id: gameState.sessionId });
      setGameState((prev) => ({
        ...prev,
        question: data.question,
        progression: data.progression,
        step: data.step,
        loading: false,
        error: null
      }));
    } catch (error) {
      console.error('Error going back:', error);
      setGameState((prev) => ({
        ...prev,
        loading: false,
        error: 'Не удалось вернуться на предыдущий вопрос.'
      }));
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
        {gameState.error && (
          <Div>
            <Text style={{ color: 'var(--vkui--color_text_negative)' }}>{gameState.error}</Text>
          </Div>
        )}
        {!gameState.sessionId ? (
          <Div>
            <Button stretched size="l" mode="primary" onClick={startGame} disabled={gameState.loading}>
              {gameState.loading ? 'Загрузка...' : 'Начать игру'}
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
