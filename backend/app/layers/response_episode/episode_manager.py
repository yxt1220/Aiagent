from app.layers.response_episode.episode_schema import EpisodeState
from app.layers.response_episode.state_tracker import update_episode_state


class EpisodeManager:
    def __init__(self):
        self.episode_state = EpisodeState.new_episode()

    def get_state(self) -> EpisodeState:
        return self.episode_state

    def reset(self, episode_id: str = "ep_001"):
        self.episode_state = EpisodeState.new_episode(episode_id=episode_id)

    def update(
        self,
        user_input,
        diagnosis,
        routing,
        pedagogy,
        assistant_response
    ) -> EpisodeState:
        self.episode_state = update_episode_state(
            episode_state=self.episode_state,
            user_input=user_input,
            diagnosis=diagnosis,
            routing=routing,
            pedagogy=pedagogy,
            assistant_response=assistant_response,
        )
        return self.episode_state