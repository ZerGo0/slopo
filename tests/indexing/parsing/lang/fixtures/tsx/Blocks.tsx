export function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "increment":
      return { ...state, count: state.count + 1 };
    case "reset":
      state = initialState;
      return state;
    default:
      return state;
  }
}

export async function loadUser(id: number): Promise<User> {
  let user: User;
  try {
    const res = await fetch(`/users/${id}`);
    user = await res.json();
  } catch (err) {
    log(err);
    user = guestUser();
  }
  return user;
}
