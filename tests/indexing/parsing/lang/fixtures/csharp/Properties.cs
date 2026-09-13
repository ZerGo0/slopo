namespace Accounts;

public class Account
{
    private decimal _balance;
    private string _owner = "";

    public decimal Balance
    {
        get
        {
            return _balance;
        }
        set
        {
            decimal rounded = decimal.Round(value, 2);
            _balance = rounded;
        }
    }

    public string Owner
    {
        get => _owner;
        set => _owner = value.Trim();
    }

    public bool Overdrawn { get; set; }
}
