import { render, screen, fireEvent } from '@testing-library/react';
import { TodoList } from '../TodoList';

describe('TodoList', () => {
  it('renders the todo list', () => {
    render(<TodoList />);
    expect(screen.getByText('Todo List')).toBeInTheDocument();
    expect(screen.getByTestId('todo-input')).toBeInTheDocument();
    expect(screen.getByTestId('add-todo-button')).toBeInTheDocument();
  });

  it('adds a new todo', () => {
    render(<TodoList />);
    const input = screen.getByTestId('todo-input');
    const addButton = screen.getByTestId('add-todo-button');

    fireEvent.change(input, { target: { value: 'New Todo' } });
    fireEvent.click(addButton);

    expect(screen.getByTestId('todo-item')).toBeInTheDocument();
    expect(screen.getByText('New Todo')).toBeInTheDocument();
  });

  it('toggles todo completion', () => {
    render(<TodoList />);
    const input = screen.getByTestId('todo-input');
    const addButton = screen.getByTestId('add-todo-button');

    fireEvent.change(input, { target: { value: 'Toggle Todo' } });
    fireEvent.click(addButton);

    const todoItem = screen.getByTestId('todo-item');
    const checkbox = screen.getByRole('checkbox');

    fireEvent.click(checkbox);
    expect(todoItem.querySelector('span')).toHaveClass('line-through');

    fireEvent.click(checkbox);
    expect(todoItem.querySelector('span')).not.toHaveClass('line-through');
  });

  it('deletes a todo', () => {
    render(<TodoList />);
    const input = screen.getByTestId('todo-input');
    const addButton = screen.getByTestId('add-todo-button');

    fireEvent.change(input, { target: { value: 'Delete Todo' } });
    fireEvent.click(addButton);

    const deleteButton = screen.getByText('Delete');
    fireEvent.click(deleteButton);

    expect(screen.queryByText('Delete Todo')).not.toBeInTheDocument();
  });

  it('does not add empty todos', () => {
    render(<TodoList />);
    const addButton = screen.getByTestId('add-todo-button');

    fireEvent.click(addButton);
    expect(screen.queryByTestId('todo-item')).not.toBeInTheDocument();
  });
});