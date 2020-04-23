from rest_framework.decorators import action
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from core.models import Stock, Portfolio, Holding, Transaction, DailyPrice
from portfolio import serializers
from core.data.data import update_stock

# maybe update holdings and portfolio helper functions


class ListStocks(APIView):
    """View for retrieving all stocks"""
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        """Return all stocks in the database"""
        stocks = Stock.objects.all()
        serializer = serializers.StockSerializer(stocks, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new stock object in the database"""
        serializer = serializers.StockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    def get_permissions(self):
        """Override get_permissions so only admins can create new stocks"""
        is_admin = IsAdminUser()
        is_authenticated = IsAuthenticated()
        if self.request.method == 'POST':
            return [is_admin]
        else:
            return [is_authenticated]


class StockDetail(APIView):
    """View for retrieving stock detail"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, ticker):
        """Return a detail view of a stock"""
        try:
            stock = Stock.objects.get(ticker=ticker)
        except Stock.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.StockSerializer(stock)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class PortfolioView(APIView):
    """Create a portfolio and retrieve all portfolios for a user"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """return portfolios assigned to user"""
        print("hit endpoint")
        portfolios = Portfolio.objects.filter(
            user=self.request.user).distinct()
        serializer = serializers.PortfolioSerializer(portfolios, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
        

    def post(self, request):
        """Create a new portfolio"""
        serializer = serializers.PortfolioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class PortfolioDetailView(APIView):
    """View for retrieving portfolio detail and updating portfolio"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """get portfolio detail"""
        try:
            portfolio = Portfolio.objects.get(id=id)
        except Portoflio.DoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)

        if self.request.user != portfolio.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = serializers.PortfolioSerializer(portfolio)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def patch(self, request, id):
        """Update name/balance of a portfolio"""
        try:
            portfolio = Portfolio.objects.get(id=id)
        except Portoflio.DoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)

        if self.request.user != portfolio.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = serializers.PortfolioSerializer(portfolio, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        return Response(status.HTTP_400_BAD_REQUEST)


class TransactionView(APIView):
    """View for retrieving and posting transactions"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """Return the transactions associated with the portfolio id given"""
        try:
            portfolio = Portfolio.objects.get(user=self.request.user, id=id)
        except Portfolio.DoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)

        if self.request.user != portfolio.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        transactions = Transaction.objects.filter(portfolio=portfolio)
        serializer = serializers.TransactionSerializer(transactions, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def post(self, request, id):
        """Allow a user to post transactions aka buy or sell a stock"""

        try:
            portfolio = Portfolio.objects.get(id=id)
        except Portfolio.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if self.request.user != portfolio.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            stock = Stock.objects.get(ticker=request.data['ticker'])
        except Stock.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            holding = Holding.objects.filter(
                portfolio=portfolio).get(stock=stock)
        except Holding.DoesNotExist:
            holding = None
        
        if request.data['order_type'] == 'Market':
            #update_stock(stock)
            ##add try except
            request.data['price'] = 1#DailyPrice.objects.filter(stock=stock).latest('time_stamp').close_price

        context = {'portfolio': portfolio, 'stock': stock, 'holding': holding}
        serializer = serializers.TransactionSerializer(
            data=request.data, context=context)
        print(request.data)

        if serializer.is_valid():
            num_shares = int(request.data['number_of_shares'])
            price = float(request.data['price'])*num_shares

            if request.data['is_buy'] == True:
                if holding is None:
                    Holding.objects.create(
                        portfolio=portfolio,
                        stock=stock,
                        number_of_shares=num_shares
                    )
                else:
                    holding.number_of_shares = int(
                        holding.number_of_shares)+num_shares
                    holding.save()
                portfolio.balance = float(portfolio.balance)-price
            else:
                if num_shares == int(holding.number_of_shares):
                    holding.delete()
                else:
                    holding.number_of_shares = int(
                        holding.number_of_shares)-num_shares
                    holding.save()
                portfolio.balance = float(portfolio.balance)+price
            serializer.save(stock=stock, portfolio=portfolio)
            portfolio.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        print(str(Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)))
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionDetailView(APIView):
    """Transaction Detail View"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """Return transaction detail view for transaction with id"""
        try:
            transaction = Transaction.objects.get(id=id)
        except Transaction.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if self.request.user != transaction.portfolio.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = serializers.TransactionSerializer(transaction)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

class HoldingView(APIView):
    """Endpoint for holding objects"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """Return holding objects associated with portfolio_id"""
        try:
            portfolio = Portfolio.objects.get(id=id)
        except Portfolio.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        holdings = Holding.objects.filter(portfolio=portfolio)
        serializer = serializers.HoldingSerializer(holdings, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


